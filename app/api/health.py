from fastapi import APIRouter
from app.models.food_truck import HealthResponse
from datetime import datetime

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running
    """
    return HealthResponse(
        status="healthy",
        service="Food Truck Search API",
        timestamp=datetime.now().isoformat()
    )
