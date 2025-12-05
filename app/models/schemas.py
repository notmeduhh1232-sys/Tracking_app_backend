from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    MOCK = "mock"
    REAL = "real"
    GPS_FALLBACK = "gps_fallback"

class NetworkType(str, Enum):
    GSM = "GSM"
    LTE = "LTE"
    WCDMA = "WCDMA"

class CellTowerData(BaseModel):
    cid: int
    lac: int
    mcc: int
    mnc: int
    rssi: int
    ta: Optional[int] = None
    type: Optional[str] = None
    distance: Optional[int] = None

class RawCellData(BaseModel):
    cells: List[CellTowerData]
    mcc: Optional[int] = None
    mnc: Optional[int] = None

class Position(BaseModel):
    lat: float
    lon: float

class PositionUpdate(BaseModel):
    vehicle_id: str
    route_id: Optional[str] = None
    timestamp: str
    raw_data: RawCellData
    device_type: DeviceType = DeviceType.MOCK
    position: Optional[Position] = None  # For demo mode

class EstimatedPosition(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class PositionResponse(BaseModel):
    id: str
    vehicle_id: str
    route_id: Optional[str] = None
    timestamp: datetime
    estimated_position: EstimatedPosition
    accuracy: float
    method: str
    device_type: str

class Stop(BaseModel):
    id: str
    name: str
    lat: float
    lon: float

class RouteSegment(BaseModel):
    start_stop: str
    end_stop: str
    path: List[Position]
    length: float
    statistics: Optional[Dict[str, Any]] = None

class Route(BaseModel):
    route_id: str
    name: str
    stops: List[Stop]
    segments: List[RouteSegment]

class Vehicle(BaseModel):
    device_id: str
    route_id: Optional[str] = None
    status: str = "active"
    last_update: Optional[datetime] = None

class TowerLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class Tower(BaseModel):
    cid: int
    lac: int
    mcc: int
    mnc: int
    location: TowerLocation
    range_meters: Optional[int] = None
    network_type: Optional[NetworkType] = None
