from pydantic import BaseModel, Field
from typing import List, Optional, Union
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
    limit: Optional[int] = Field(5, ge=1, le=100, description="Maximum number of results")

class FoodTruck(BaseModel):
    """
    Represents a Mobile Food Facility Permit,
    including name of vendor, location, type of food sold and status of permit.
    """
    location_id: int = Field(..., alias="locationid", description="Location id of facility")
    permit: str = Field(..., description="Permit number")
    status: str = Field(..., alias="Status", description="Status of permit: Approved or Requested")
    food_items: Optional[str] = Field(None, alias="FoodItems", description="A description of food items sold")
    x: Optional[float] = Field(None, alias="X", description="CA State Plane III")
    y: Optional[float] = Field(None, alias="Y", description="CA State Plane III")
    latitude: Optional[float] = Field(None, alias="Latitude", description="WGS84, latitude")
    longitude: Optional[float] = Field(None, alias="Longitude", description="WGS84, longitude")
    schedule: Optional[str] = Field(None, alias="Schedule", description="URL link to Schedule for facility")
    days_hours: Optional[str] = Field(None, alias="dayshours", description="abbreviated text of schedule")
    noi_sent: Optional[str] = Field(None, alias="NOISent", description="Date notice of intent sent")
    applicant: Optional[str] = Field(None, alias="Applicant", description="Name of permit holder")
    approved: Optional[str] = Field(None, alias="Approved", description="Date permit approved by DPW")
    received: Optional[int] = Field(None, alias="Received", description="Date permit application received from applicant (YYYYMMDD format)")
    prior_permit: Optional[int] = Field(None, alias="PriorPermit", description="prior existing permit with SFFD")
    expiration_date: Optional[str] = Field(None, alias="ExpirationDate", description="Date permit expires")
    location: Optional[str] = Field(None, alias="Location", description="Location formatted for mapping")
    facility_type: Optional[str] = Field(None, alias="FacilityType", description="Type of facilty permitted: truck or push cart")
    cnn: Optional[int] = Field(None, alias="cnn", description="CNN of street segment or intersection location")
    location_description: Optional[str] = Field(None, alias="LocationDescription", description="Description of street segment or intersection location")
    address: Optional[str] = Field(None, alias="Address", description="Address")
    blocklot: Optional[str] = Field(None, alias="blocklot", description="Block lot (parcel) number")
    block: Optional[str] = Field(None, alias="block", description="Block number")
    lot: Optional[str] = Field(None, alias="lot", description="Lot number")

    class Config:
        allow_population_by_field_name = True
        extra = 'ignore'

class SearchResponse(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    message: str = Field(..., description="Response message")
    data: List[FoodTruck] = Field(..., description="List of food trucks")
    metadata: dict = Field(..., description="Search metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")
