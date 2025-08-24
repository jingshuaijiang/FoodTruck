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
    # Replace NaN values with None for proper JSON serialization
    df_clean = df.replace({float('nan'): None})
    
    # Convert to list of dictionaries and create FoodTruck objects
    data_dicts = df_clean.to_dict('records')
    food_trucks = [FoodTruck(**data_dict) for data_dict in data_dicts]
    
    # Convert to JSON and back to ensure proper field names are used
    # This ensures the Pydantic model field names (not aliases) are used in the response
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
