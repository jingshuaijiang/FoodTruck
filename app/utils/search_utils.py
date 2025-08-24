import pandas as pd
from typing import List, Tuple
from app.models.food_truck import FoodTruck, SearchType, StatusType
from app.utils.geo import haversine_distance

def apply_status_filter(df: pd.DataFrame, status: StatusType = None) -> pd.DataFrame:
    """
    Apply status filter to DataFrame.
    
    Args:
        df: DataFrame containing food truck data
        status: Status to filter by
    
    Returns:
        Filtered DataFrame
    """
    if status:
        return df[df['Status'] == status.value].copy()
    return df.copy()

def search_by_name(df: pd.DataFrame, applicant: str, status: StatusType = None) -> pd.DataFrame:
    """
    Search food trucks by business name.
    
    Args:
        df: DataFrame containing food truck data
        applicant: Business name to search for
        status: Optional status filter
    
    Returns:
        Filtered DataFrame
    """
    if not applicant:
        raise ValueError("Applicant name required for name search")
    
    # Apply status filter
    df = apply_status_filter(df, status)
    
    mask = df['Applicant'].str.contains(applicant, case=False, na=False)
    return df[mask]

def search_by_street(df: pd.DataFrame, street: str, status: StatusType = None) -> pd.DataFrame:
    """
    Search food trucks by street address.
    
    Args:
        df: DataFrame containing food truck data
        street: Street name to search for
        status: Optional status filter
    
    Returns:
        Filtered DataFrame
    """
    if not street:
        raise ValueError("Street name required for street search")
    
    # Apply status filter
    df = apply_status_filter(df, status)
    
    mask = df['Address'].str.contains(street, case=False, na=False)
    return df[mask]

def search_by_proximity(df: pd.DataFrame, latitude: float, longitude: float, status: StatusType = StatusType.APPROVED) -> pd.DataFrame:
    """
    Search food trucks by proximity to coordinates.
    
    Args:
        df: DataFrame containing food truck data
        latitude: Search latitude
        longitude: Search longitude
        status: Optional status filter (defaults to APPROVED)
    
    Returns:
        Filtered and sorted DataFrame by distance
    """
    if latitude is None or longitude is None:
        raise ValueError("Latitude and longitude required for proximity search")
    
    # Apply status filter (defaults to APPROVED if not specified)
    df = apply_status_filter(df, status)
    
    # Copy the DataFrame first, then filter to only rows with valid coordinates
    df_copy = df.copy()
    valid_coords_df = df_copy.dropna(subset=['Latitude', 'Longitude'])
    
    if valid_coords_df.empty:
        return valid_coords_df  # Return empty DataFrame if no valid coordinates
    
    # Calculate distances and sort by proximity
    valid_coords_df['Distance'] = valid_coords_df.apply(
        lambda row: haversine_distance(
            latitude, longitude,
            row['Latitude'], row['Longitude']
        ), axis=1
    )
    return valid_coords_df.sort_values('Distance')

