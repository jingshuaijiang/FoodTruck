import pandas as pd
from typing import List
from app.models.food_truck import FoodTruck, SearchType, StatusType

def convert_to_food_trucks(df: pd.DataFrame) -> List[FoodTruck]:
    """
    Convert DataFrame rows to FoodTruck objects.
    
    Args:
        df: DataFrame containing food truck data
    
    Returns:
        List of FoodTruck objects
    """
    food_trucks = []
    for _, row in df.iterrows():
        food_truck = FoodTruck(
            locationid=str(row['locationid']),
            applicant=str(row['applicant']),
            facility_type=str(row['facilitytype']),
            address=str(row['address']),
            status=str(row['status']),
            food_items=str(row['fooditems']),
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            location_description=row.get('locationdescription')
        )
        food_trucks.append(food_truck)
    
    return food_trucks

def create_search_metadata(query_type: SearchType, status: StatusType = None, limit: int = 10, 
                          latitude: float = None, longitude: float = None) -> dict:
    """
    Create metadata for search response.
    
    Args:
        query_type: Type of search performed
        status: Status filter applied
        limit: Result limit
        latitude: Search latitude (for proximity searches)
        longitude: Search longitude (for proximity searches)
    
    Returns:
        Metadata dictionary
    """
    metadata = {
        "query_type": query_type.value,
        "status_filter": status.value if status else None,
        "limit": limit
    }
    
    if query_type == SearchType.PROXIMITY:
        metadata["search_coordinates"] = {
            "latitude": latitude,
            "longitude": longitude
        }
    
    return metadata
