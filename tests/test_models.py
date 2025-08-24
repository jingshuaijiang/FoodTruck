import pytest
from pydantic import ValidationError
from app.models.food_truck import (
    SearchType, StatusType, SearchRequest, FoodTruck, 
    SearchResponse, HealthResponse
)


class TestSearchType:
    def test_valid_search_types(self):
        """Test that all search types are valid"""
        assert SearchType.NAME == "name"
        assert SearchType.STREET == "street"
        assert SearchType.PROXIMITY == "proximity"

    def test_search_type_values(self):
        """Test that search type values are strings"""
        for search_type in SearchType:
            assert isinstance(search_type.value, str)


class TestStatusType:
    def test_valid_status_types(self):
        """Test that all status types are valid"""
        assert StatusType.APPROVED == "APPROVED"
        assert StatusType.REQUESTED == "REQUESTED"
        assert StatusType.EXPIRED == "EXPIRED"

    def test_status_type_values(self):
        """Test that status type values are strings"""
        for status_type in StatusType:
            assert isinstance(status_type.value, str)


class TestSearchRequest:
    def test_valid_name_search(self):
        """Test valid name search request"""
        request = SearchRequest(
            query_type=SearchType.NAME,
            applicant="Taco Truck"
        )
        assert request.query_type == SearchType.NAME
        assert request.applicant == "Taco Truck"
        assert request.street is None
        assert request.latitude is None
        assert request.longitude is None
        assert request.status is None

    def test_valid_street_search(self):
        """Test valid street search request"""
        request = SearchRequest(
            query_type=SearchType.STREET,
            street="Mission St"
        )
        assert request.query_type == SearchType.STREET
        assert request.street == "Mission St"
        assert request.applicant is None

    def test_valid_proximity_search(self):
        """Test valid proximity search request"""
        request = SearchRequest(
            query_type=SearchType.PROXIMITY,
            latitude=37.7749,
            longitude=-122.4194
        )
        assert request.query_type == SearchType.PROXIMITY
        assert request.latitude == 37.7749
        assert request.longitude == -122.4194

    def test_search_with_status_filter(self):
        """Test search request with status filter"""
        request = SearchRequest(
            query_type=SearchType.NAME,
            applicant="Taco",
            status=StatusType.APPROVED
        )
        assert request.status == StatusType.APPROVED

    def test_search_with_custom_limit(self):
        """Test search request with custom limit"""
        request = SearchRequest(
            query_type=SearchType.NAME,
            applicant="Taco",
            limit=25
        )
        assert request.limit == 25

    def test_invalid_latitude_range(self):
        """Test that latitude must be within valid range"""
        with pytest.raises(ValidationError):
            SearchRequest(
                query_type=SearchType.PROXIMITY,
                latitude=100.0,  # Invalid latitude
                longitude=-122.4194
            )

    def test_invalid_longitude_range(self):
        """Test that longitude must be within valid range"""
        with pytest.raises(ValidationError):
            SearchRequest(
                query_type=SearchType.PROXIMITY,
                latitude=37.7749,
                longitude=200.0  # Invalid longitude
            )

    def test_invalid_limit_range(self):
        """Test that limit must be within valid range"""
        with pytest.raises(ValidationError):
            SearchRequest(
                query_type=SearchType.NAME,
                applicant="Taco",
                limit=0  # Invalid limit
            )


class TestFoodTruck:
    def test_valid_food_truck(self):
        """Test valid food truck creation"""
        truck = FoodTruck(
            locationid=12345,
            permit="24MFF-00001",
            Status="APPROVED",
            Applicant="Test Truck",
            Address="123 Test St",
            Latitude=37.7749,
            Longitude=-122.4194
        )
        assert truck.location_id == 12345
        assert truck.permit == "24MFF-00001"
        assert truck.status == "APPROVED"
        assert truck.applicant == "Test Truck"
        assert truck.address == "123 Test St"
        assert truck.latitude == 37.7749
        assert truck.longitude == -122.4194

    def test_food_truck_with_aliases(self):
        """Test that aliases work correctly"""
        truck = FoodTruck(
            locationid=12345,
            permit="24MFF-00001",
            Status="REQUESTED",
            Applicant="Test Truck"
        )
        assert truck.status == "REQUESTED"
        assert truck.applicant == "Test Truck"

    def test_food_truck_optional_fields(self):
        """Test food truck with optional fields"""
        truck = FoodTruck(
            locationid=12345,
            permit="24MFF-00001",
            Status="APPROVED"
        )
        assert truck.food_items is None
        assert truck.facility_type is None
        assert truck.latitude is None

    def test_food_truck_received_field_as_int(self):
        """Test that Received field can be integer"""
        truck = FoodTruck(
            locationid=12345,
            permit="24MFF-00001",
            Status="APPROVED",
            Received=20241118
        )
        assert truck.received == 20241118


class TestSearchResponse:
    def test_valid_search_response(self):
        """Test valid search response creation"""
        response = SearchResponse(
            success=True,
            message="Search completed successfully",
            data=[],
            metadata={"total_results": 0}
        )
        assert response.success is True
        assert response.message == "Search completed successfully"
        assert response.data == []
        assert response.metadata["total_results"] == 0


class TestHealthResponse:
    def test_valid_health_response(self):
        """Test valid health response creation"""
        response = HealthResponse(
            status="healthy",
            service="Food Truck Search API",
            timestamp="2024-01-01T00:00:00"
        )
        assert response.status == "healthy"
        assert response.service == "Food Truck Search API"
        assert response.timestamp == "2024-01-01T00:00:00"
