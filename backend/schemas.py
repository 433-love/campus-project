from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class CatCreate(BaseModel):
    name: str
    profile_image_url: Optional[str] = None
    description: Optional[str] = None
    health_status: Optional[str] = None


class CatUpdate(BaseModel):
    name: Optional[str] = None
    profile_image_url: Optional[str] = None
    description: Optional[str] = None
    health_status: Optional[str] = None


class CatSummary(BaseModel):
    cat_id: int
    name: str
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class SightingCreate(BaseModel):
    user_id: Optional[int] = None
    cat_id: int
    location: str
    photo_url: Optional[str] = None


class FeedingCreate(BaseModel):
    user_id: Optional[int] = None
    cat_id: int
    food_type: str
    amount: str


class TimelineItem(BaseModel):
    type: Literal["sighting", "feeding"]
    timestamp: datetime
    data: dict


class TrackingDeviceCreate(BaseModel):
    cat_id: int
    device_type: str
    device_name: str
    device_serial: str
    battery_level: Optional[int] = None


class TrackingDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    battery_level: Optional[int] = None
    is_active: Optional[int] = None


class TrackingDeviceResponse(BaseModel):
    device_id: int
    cat_id: int
    device_type: str
    device_name: str
    device_serial: str
    battery_level: Optional[int] = None
    is_active: int
    registered_date: datetime

    class Config:
        from_attributes = True


class TrackingLogCreate(BaseModel):
    device_id: int
    cat_id: int
    latitude: str
    longitude: str
    location_name: Optional[str] = None


class TrackingLogResponse(BaseModel):
    log_id: int
    device_id: int
    cat_id: int
    latitude: str
    longitude: str
    location_name: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True