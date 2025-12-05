"""
Route Tracking Service
Converts raw position data to passenger-friendly stop status and ETAs
"""
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RouteTrackingService:
    """Service to track bus progress along routes and calculate ETAs"""
    
    def __init__(self):
        self.EARTH_RADIUS = 6371  # km
        self.AVERAGE_SPEED = 40  # km/h (bus average speed)
        self.ROAD_FACTOR = 1.3  # Roads aren't straight
        self.AT_STOP_THRESHOLD = 0.3  # km (300m = "at stop")
        
        # Route definitions with stops
        self.routes = {
            "route_101": {
                "id": "route_101",
                "name": "KP-1 to KP-3 Express",
                "stops": [
                    {
                        "id": "stop_101",
                        "name": "KP-1 Gate",
                        "lat": 28.4744,
                        "lon": 77.4860,
                        "sequence": 1
                    },
                    {
                        "id": "stop_102",
                        "name": "GL Bajaj",
                        "lat": 28.4715,
                        "lon": 77.4885,
                        "sequence": 2
                    },
                    {
                        "id": "stop_103",
                        "name": "KP-2 Main Gate",
                        "lat": 28.4686,
                        "lon": 77.4950,
                        "sequence": 3
                    },
                    {
                        "id": "stop_104",
                        "name": "Alpha 1 Hub",
                        "lat": 28.4670,
                        "lon": 77.4980,
                        "sequence": 4
                    },
                    {
                        "id": "stop_105",
                        "name": "KP-3 Entrance",
                        "lat": 28.4640,
                        "lon": 77.5045,
                        "sequence": 5
                    }
                ]
            },
            "route_102": {
                "id": "route_102",
                "name": "KP-2 Circular",
                "stops": [
                    {
                        "id": "stop_201",
                        "name": "KP-2 Gate 1",
                        "lat": 28.4686,
                        "lon": 77.4950,
                        "sequence": 1
                    },
                    {
                        "id": "stop_202",
                        "name": "BIMTECH",
                        "lat": 28.4625,
                        "lon": 77.5080,
                        "sequence": 2
                    },
                    {
                        "id": "stop_203",
                        "name": "Pari Chowk",
                        "lat": 28.4744,
                        "lon": 77.4860,
                        "sequence": 3
                    },
                    {
                        "id": "stop_204",
                        "name": "KP-2 Gate 2",
                        "lat": 28.4686,
                        "lon": 77.4950,
                        "sequence": 4
                    }
                ]
            }
        }
    
    async def process_position_update(
        self,
        vehicle_id: str,
        route_id: str,
        position: Dict[str, float],
        accuracy: float,
        method: str,
        timestamp: str,
        raw_data: Optional[Dict] = None
    ) -> Dict:
        """
        Main processing function - converts position to passenger-friendly data
        
        Args:
            vehicle_id: Driver/vehicle identifier
            route_id: Route being traveled
            position: {"lat": float, "lon": float}
            accuracy: Position accuracy in meters
            method: Positioning method used
            timestamp: ISO timestamp
            raw_data: Optional raw cellular data for technical details
        
        Returns:
            Passenger-friendly data with stop status and ETAs
        """
        try:
            # Get route information
            route = self.routes.get(route_id)
            if not route:
                logger.warning(f"Route {route_id} not found")
                return self._create_error_response("Route not found")
            
            # Extract coordinates
            lat = position.get("lat")
            lon = position.get("lon")
            if lat is None or lon is None:
                logger.warning("Invalid position data")
                return self._create_error_response("Invalid position")
            
            # Find closest stop and determine progress
            current_stop_index = self._find_closest_stop(lat, lon, route["stops"])
            
            # Calculate status for all stops
            stops_status = self._calculate_stops_status(
                lat, lon, route["stops"], current_stop_index
            )
            
            # Calculate ETAs for upcoming stops
            stops_with_eta = self._calculate_etas(
                lat, lon, route["stops"], current_stop_index, timestamp
            )
            
            # Build response
            response = {
                "vehicle_id": vehicle_id,
                "route_id": route_id,
                "route_name": route["name"],
                "timestamp": timestamp,
                "current_stop": route["stops"][current_stop_index]["name"],
                "current_stop_id": route["stops"][current_stop_index]["id"],
                "stops": stops_with_eta,
                "positioning": {
                    "accuracy": accuracy,
                    "method": method
                }
            }
            
            # Add technical details for live mode
            if raw_data:
                response["technical_details"] = self._build_technical_details(
                    raw_data, position, accuracy, method
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing position update: {e}")
            return self._create_error_response(str(e))
    
    def _find_closest_stop(
        self, 
        lat: float, 
        lon: float, 
        stops: List[Dict]
    ) -> int:
        """Find the index of the closest stop to current position"""
        min_distance = float('inf')
        closest_index = 0
        
        for i, stop in enumerate(stops):
            distance = self._haversine_distance(
                lat, lon, stop["lat"], stop["lon"]
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        return closest_index
    
    def _calculate_stops_status(
        self,
        lat: float,
        lon: float,
        stops: List[Dict],
        current_stop_index: int
    ) -> List[Dict]:
        """Determine status (completed/current/upcoming) for each stop"""
        stops_status = []
        
        for i, stop in enumerate(stops):
            distance = self._haversine_distance(
                lat, lon, stop["lat"], stop["lon"]
            )
            
            # Determine status
            if distance < self.AT_STOP_THRESHOLD:
                status = "current"
            elif i < current_stop_index:
                status = "completed"
            else:
                status = "upcoming"
            
            stops_status.append({
                "id": stop["id"],
                "name": stop["name"],
                "status": status,
                "distance_km": round(distance, 2)
            })
        
        return stops_status
    
    def _calculate_etas(
        self,
        lat: float,
        lon: float,
        stops: List[Dict],
        current_stop_index: int,
        timestamp: str
    ) -> List[Dict]:
        """Calculate ETAs for all stops"""
        stops_with_eta = []
        current_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        cumulative_time = 0
        
        for i, stop in enumerate(stops):
            stop_data = {
                "id": stop["id"],
                "name": stop["name"],
                "sequence": stop["sequence"]
            }
            
            if i < current_stop_index:
                # Completed stops
                stop_data["status"] = "completed"
                # Estimate time ago (rough calculation)
                stops_passed = current_stop_index - i
                minutes_ago = stops_passed * 3  # Assume 3 mins per stop
                stop_data["time_ago"] = minutes_ago
                
            elif i == current_stop_index:
                # Current stop
                stop_data["status"] = "current"
                distance = self._haversine_distance(
                    lat, lon, stop["lat"], stop["lon"]
                )
                if distance < self.AT_STOP_THRESHOLD:
                    stop_data["at_stop"] = True
                else:
                    stop_data["at_stop"] = False
                    stop_data["distance_km"] = round(distance, 2)
                
            else:
                # Upcoming stops
                stop_data["status"] = "upcoming"
                
                # Calculate distance
                if i == current_stop_index + 1:
                    # Next stop - direct distance from current position
                    distance = self._haversine_distance(
                        lat, lon, stop["lat"], stop["lon"]
                    )
                else:
                    # Further stops - distance from previous stop
                    prev_stop = stops[i - 1]
                    distance = self._haversine_distance(
                        prev_stop["lat"], prev_stop["lon"],
                        stop["lat"], stop["lon"]
                    )
                
                # Apply road factor
                road_distance = distance * self.ROAD_FACTOR
                
                # Calculate time in minutes
                time_minutes = (road_distance / self.AVERAGE_SPEED) * 60
                
                # Add stop time (1 minute per intermediate stop)
                if i > current_stop_index + 1:
                    time_minutes += 1
                
                cumulative_time += time_minutes
                
                # Calculate ETA
                eta_time = current_time + timedelta(minutes=cumulative_time)
                
                stop_data["distance_km"] = round(road_distance, 2)
                stop_data["eta_minutes"] = round(cumulative_time)
                stop_data["eta_time"] = eta_time.strftime("%H:%M")
            
            stops_with_eta.append(stop_data)
        
        return stops_with_eta
    
    def _build_technical_details(
        self,
        raw_data: Dict,
        position: Dict,
        accuracy: float,
        method: str
    ) -> Dict:
        """Build technical details for live mode display"""
        technical = {
            "position_calculation": {
                "method": method,
                "accuracy_meters": accuracy,
                "coordinates": position
            }
        }
        
        # Add cellular data if available
        if "cells" in raw_data:
            cells = raw_data["cells"]
            
            # Serving cell (strongest signal)
            serving_cell = cells[0] if cells else None
            if serving_cell:
                technical["serving_cell"] = {
                    "cid": serving_cell.get("cid"),
                    "lac": serving_cell.get("lac"),
                    "rssi": serving_cell.get("rssi"),
                    "signal_quality": self._get_signal_quality(serving_cell.get("rssi", -100)),
                    "distance": serving_cell.get("distance")
                }
            
            # Neighbor cells
            if len(cells) > 1:
                technical["neighbor_cells"] = [
                    {
                        "cid": cell.get("cid"),
                        "rssi": cell.get("rssi"),
                        "distance": cell.get("distance")
                    }
                    for cell in cells[1:6]  # Max 5 neighbors
                ]
            
            technical["towers_detected"] = len(cells)
            technical["network"] = f"{raw_data.get('mcc', '?')}-{raw_data.get('mnc', '?')}"
        
        return technical
    
    def _get_signal_quality(self, rssi: int) -> str:
        """Convert RSSI to human-readable signal quality"""
        if rssi >= -70:
            return "Excellent"
        elif rssi >= -85:
            return "Good"
        elif rssi >= -100:
            return "Fair"
        else:
            return "Poor"
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points in km"""
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
        
        return distance
    
    def _create_error_response(self, error: str) -> Dict:
        """Create error response"""
        return {
            "error": error,
            "stops": []
        }
    
    async def get_route_info(self, route_id: str) -> Optional[Dict]:
        """Get route information"""
        return self.routes.get(route_id)
    
    async def list_all_routes(self) -> List[Dict]:
        """List all available routes"""
        return [
            {
                "id": route_id,
                "name": route["name"],
                "stops_count": len(route["stops"])
            }
            for route_id, route in self.routes.items()
        ]

# Global instance
route_tracking_service = RouteTrackingService()
