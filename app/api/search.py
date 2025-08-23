from fastapi import APIRouter, HTTPException
from app.models.food_truck import SearchRequest, SearchResponse, SearchType
from app.dataloader.food_truck_loader import data_loader
from app.utils.search_utils import (
    search_by_name, 
    search_by_street, 
    search_by_proximity, 
    apply_status_filter
)
from app.utils.mappers import convert_to_food_trucks, create_search_metadata

router = APIRouter()

@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_food_trucks(search_request: SearchRequest):
    """
    Search for food trucks by name, street, or proximity
    
    - **query_type**: Type of search (name, street, or proximity)
    - **applicant**: Business name for name search
    - **street**: Street name for street search  
    - **latitude**: Latitude for proximity search
    - **longitude**: Longitude for proximity search
    - **status**: Optional status filter
    - **limit**: Maximum number of results (default: 10, max: 100)
    """
    try:
        # Get data from loader with auto-reload
        df = data_loader.get_data()
        if not data_loader.is_data_available():
            raise HTTPException(status_code=500, detail="Data not available")
        
        # Perform search based on query type
        if search_request.query_type == SearchType.NAME:
            filtered_df = search_by_name(df, search_request.applicant, search_request.status)
        elif search_request.query_type == SearchType.STREET:
            filtered_df = search_by_street(df, search_request.street, search_request.status)
        elif search_request.query_type == SearchType.PROXIMITY:
            filtered_df = search_by_proximity(df, search_request.latitude, search_request.longitude, search_request.status)
        
        # Limit results - different defaults based on search type
        if search_request.query_type == SearchType.PROXIMITY:
            limit = search_request.limit or 5  # Default 5 for proximity search
        else:
            limit = search_request.limit or 10  # Default 10 for name/street search
        filtered_df = filtered_df.head(limit)
        
        # Convert to FoodTruck objects
        results = convert_to_food_trucks(filtered_df)
        
        # Create metadata
        metadata = create_search_metadata(
            search_request.query_type,
            search_request.status,
            limit,
            search_request.latitude,
            search_request.longitude
        )
        metadata["total_results"] = len(results)
        
        return SearchResponse(
            success=True,
            message=f"Search completed successfully. Found {len(results)} results.",
            data=results,
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
