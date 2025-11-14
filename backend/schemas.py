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