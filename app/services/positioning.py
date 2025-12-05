import math
import numpy as np
from typing import List, Tuple, Optional, Dict
from app.models.schemas import CellTowerData, Position
import logging

logger = logging.getLogger(__name__)

class PositioningEngine:
    """
    Implements hierarchical positioning strategy:
    1. Triangulation with Timing Advance (best: 150-200m)
    2. Weighted Centroid with RSSI (good: 300-500m)
    3. Cell-ID Fallback (basic: 500-1000m)
    """
    
    def __init__(self):
        self.EARTH_RADIUS = 6371000  # meters
        self.TA_UNIT_DISTANCE = 550  # meters (GSM TA unit)
        self.PATH_LOSS_EXPONENT = 0.22  # Urban environment
        self.REFERENCE_DISTANCE = 100  # meters
        
    async def estimate_position(
        self,
        cells: List[CellTowerData],
        tower_locations: Dict[int, Tuple[float, float]]
    ) -> Tuple[Position, float, str]:
        """
        Main position estimation method
        Returns: (position, accuracy_meters, method_used)
        """
        
        if not cells or not tower_locations:
            return None, 0, "no_data"
        
        # Filter cells that have known tower locations
        valid_cells = [
            cell for cell in cells 
            if cell.cid in tower_locations
        ]
        
        if not valid_cells:
            return None, 0, "no_tower_data"
        
        # Hierarchical positioning strategy
        
        # Tier 1: Triangulation with Timing Advance
        if len(valid_cells) >= 3 and any(cell.ta is not None for cell in valid_cells):
            position, accuracy = await self.triangulation_with_ta(valid_cells, tower_locations)
            if position:
                return position, accuracy, "triangulation_ta"
        
        # Tier 2: Weighted Centroid with RSSI
        if len(valid_cells) >= 2:
            if len(valid_cells) >= 3 and self.is_high_density(tower_locations):
                # Use Crude Estimation Method for dense areas
                position, accuracy = await self.crude_estimation_method(valid_cells, tower_locations)
                if position:
                    return position, accuracy, "crude_estimation"
            
            # Use weighted centroid
            position, accuracy = await self.weighted_centroid(valid_cells, tower_locations)
            if position:
                return position, accuracy, "weighted_centroid"
        
        # Tier 3: Cell-ID Fallback
        serving_cell = valid_cells[0]  # Strongest signal
        tower_loc = tower_locations[serving_cell.cid]
        position = Position(lat=tower_loc[0], lon=tower_loc[1])
        accuracy = 800  # Rough estimate for cell range
        return position, accuracy, "cell_id_fallback"
    
    async def triangulation_with_ta(
        self,
        cells: List[CellTowerData],
        tower_locations: Dict[int, Tuple[float, float]]
    ) -> Tuple[Optional[Position], float]:
        """Triangulation using Timing Advance"""
        
        try:
            # Get cells with TA data
            ta_cells = [cell for cell in cells if cell.ta is not None]
            if len(ta_cells) < 3:
                return None, 0
            
            # Prepare data for trilateration
            tower_coords = []
            distances = []
            
            for cell in ta_cells[:5]:  # Use up to 5 towers
                if cell.cid in tower_locations:
                    tower_lat, tower_lon = tower_locations[cell.cid]
                    tower_coords.append([tower_lat, tower_lon])
                    
                    # Convert TA to distance (meters)
                    distance = cell.ta * self.TA_UNIT_DISTANCE
                    distances.append(distance)
            
            if len(tower_coords) < 3:
                return None, 0
            
            # Solve trilateration using least squares
            position = self.trilaterate(tower_coords, distances)
            
            if position:
                accuracy = 175  # Average accuracy for TA triangulation
                return Position(lat=position[0], lon=position[1]), accuracy
            
        except Exception as e:
            logger.error(f"Triangulation error: {e}")
        
        return None, 0
    
    def trilaterate(
        self,
        tower_coords: List[List[float]],
        distances: List[float]
    ) -> Optional[List[float]]:
        """
        Solve trilateration using least squares optimization
        """
        try:
            # Convert to numpy arrays
            towers = np.array(tower_coords)
            dists = np.array(distances)
            
            # Initial guess (centroid of towers)
            x0 = np.mean(towers, axis=0)
            
            # Least squares optimization
            from scipy.optimize import least_squares
            
            def residuals(pos):
                return np.array([
                    self.haversine_distance(pos[0], pos[1], tower[0], tower[1]) - dist
                    for tower, dist in zip(towers, dists)
                ])
            
            result = least_squares(residuals, x0, method='lm')
            
            if result.success:
                return result.x.tolist()
            
        except Exception as e:
            logger.error(f"Trilateration error: {e}")
        
        return None
    
    async def weighted_centroid(
        self,
        cells: List[CellTowerData],
        tower_locations: Dict[int, Tuple[float, float]]
    ) -> Tuple[Optional[Position], float]:
        """Weighted centroid based on RSSI"""
        
        try:
            if not cells:
                return None, 0
            
            # Calculate weights based on RSSI
            max_rssi = max(cell.rssi for cell in cells)
            
            weighted_lat = 0
            weighted_lon = 0
            total_weight = 0
            
            for cell in cells:
                if cell.cid in tower_locations:
                    tower_lat, tower_lon = tower_locations[cell.cid]
                    
                    # Weight calculation: stronger signal = more weight
                    weight = 1 / ((max_rssi - cell.rssi + 1) ** self.PATH_LOSS_EXPONENT)
                    
                    weighted_lat += weight * tower_lat
                    weighted_lon += weight * tower_lon
                    total_weight += weight
            
            if total_weight == 0:
                return None, 0
            
            estimated_lat = weighted_lat / total_weight
            estimated_lon = weighted_lon / total_weight
            
            accuracy = 400  # Average accuracy for weighted centroid
            
            return Position(lat=estimated_lat, lon=estimated_lon), accuracy
            
        except Exception as e:
            logger.error(f"Weighted centroid error: {e}")
            return None, 0
    
    async def crude_estimation_method(
        self,
        cells: List[CellTowerData],
        tower_locations: Dict[int, Tuple[float, float]]
    ) -> Tuple[Optional[Position], float]:
        """
        Crude Estimation Method (CEM) based on signal strength ratios
        Best for high-density tower areas (Leung et al.)
        """
        
        try:
            if len(cells) < 3:
                return None, 0
            
            candidates = []
            
            # Generate candidate positions from pairwise tower combinations
            for i in range(len(cells)):
                for j in range(i + 1, len(cells)):
                    cell1, cell2 = cells[i], cells[j]
                    
                    if cell1.cid in tower_locations and cell2.cid in tower_locations:
                        tower1 = tower_locations[cell1.cid]
                        tower2 = tower_locations[cell2.cid]
                        
                        # Signal strength ratio
                        ratio = cell2.rssi / cell1.rssi if cell1.rssi != 0 else 1
                        
                        # Calculate candidate position along the line between towers
                        # Weighted by signal ratio
                        weight = 1 / (1 + abs(ratio))
                        
                        candidate_lat = weight * tower1[0] + (1 - weight) * tower2[0]
                        candidate_lon = weight * tower1[1] + (1 - weight) * tower2[1]
                        
                        candidates.append([candidate_lat, candidate_lon])
            
            if not candidates:
                return None, 0
            
            # Statistical filtering: remove outliers beyond ±1σ
            candidates = np.array(candidates)
            mean = np.mean(candidates, axis=0)
            std = np.std(candidates, axis=0)
            
            # Filter outliers
            filtered = []
            for candidate in candidates:
                if (abs(candidate[0] - mean[0]) <= std[0] and 
                    abs(candidate[1] - mean[1]) <= std[1]):
                    filtered.append(candidate)
            
            if not filtered:
                filtered = candidates  # Use all if filtering removes everything
            
            # Return centroid of filtered candidates
            final_position = np.mean(filtered, axis=0)
            
            accuracy = 250  # CEM typically better than weighted centroid
            
            return Position(lat=final_position[0], lon=final_position[1]), accuracy
            
        except Exception as e:
            logger.error(f"CEM error: {e}")
            return None, 0
    
    def is_high_density(self, tower_locations: Dict[int, Tuple[float, float]]) -> bool:
        """Check if tower density is high (< 800m average separation)"""
        
        if len(tower_locations) < 2:
            return False
        
        try:
            coords = list(tower_locations.values())
            
            # Calculate average distance between all tower pairs
            distances = []
            for i in range(len(coords)):
                for j in range(i + 1, len(coords)):
                    dist = self.haversine_distance(
                        coords[i][0], coords[i][1],
                        coords[j][0], coords[j][1]
                    )
                    distances.append(dist)
            
            avg_distance = np.mean(distances)
            
            return avg_distance < 800  # meters
            
        except Exception as e:
            logger.error(f"Density check error: {e}")
            return False
    
    def haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = self.EARTH_RADIUS * c
        
        return distance  # meters

# Global instance
positioning_engine = PositioningEngine()
