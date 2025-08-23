from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SearchType(str, Enum):
    NAME = "name"
    STREET = "street"
    PROXIMITY = "proximity"

class StatusType(str, Enum):
    APPROVED = "APPROVED"
    REQUESTED = "REQUESTED"
    EXPIRED = "EXPIRED"

class SearchRequest(BaseModel):
    query_type: SearchType = Field(..., description="Type of search to perform")
    applicant: Optional[str] = Field(None, description="Business name for name search")
    street: Optional[str] = Field(None, description="Street name for street search")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude for proximity search (-90 to 90)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude for proximity search (-180 to 180)")
    status: Optional[StatusType] = Field(None, description="Filter by permit status")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results")

class FoodTruck(BaseModel):
    locationid: str = Field(..., description="Unique location ID")
    applicant: str = Field(..., description="Business name")
    facility_type: str = Field(..., description="Type of facility")
    address: str = Field(..., description="Street address")
    status: str = Field(..., description="Permit status")
    food_items: str = Field(..., description="Food items served")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    location_description: Optional[str] = Field(None, description="Additional location details")

class SearchResponse(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    message: str = Field(..., description="Response message")
    data: List[FoodTruck] = Field(..., description="List of food trucks")
    metadata: dict = Field(..., description="Search metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")
