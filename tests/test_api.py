import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from app.main import app
from app.models.food_truck import SearchType, StatusType

client = TestClient(app)


class TestHealthAPI:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Food Truck Search API"
        assert "timestamp" in data


class TestSearchAPI:
    def setup_method(self):
        """Set up test data for each test method"""
        self.sample_data = pd.DataFrame({
            'locationid': [1, 2, 3],
            'Applicant': ['Taco Truck 1', 'Taco Truck 2', 'Burger Joint'],
            'Status': ['APPROVED', 'REQUESTED', 'APPROVED'],
            'Address': ['123 Mission St', '456 Market St', '789 Castro St'],
            'Latitude': [37.7749, 37.7849, 37.7649],
            'Longitude': [-122.4194, -122.4094, -122.4294],
            'FoodItems': ['Tacos, Burritos', 'Tacos, Quesadillas', 'Burgers, Fries'],
            'FacilityType': ['Truck', 'Push Cart', 'Truck'],
            'permit': ['24MFF-00001', '24MFF-00002', '24MFF-00003']
        })

    def test_search_by_name_success(self, monkeypatch):
        """Test successful name search"""
        # Create a mock data loader
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        # Monkeypatch the data_loader import in the search module
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "name",
                "applicant": "Taco"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["metadata"]["query_type"] == "name"

    def test_search_by_name_with_status_filter(self, monkeypatch):
        """Test name search with status filter"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "name",
                "applicant": "Taco",
                "status": "APPROVED"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["status_filter"] == "APPROVED"

    def test_search_by_street_success(self, monkeypatch):
        """Test successful street search"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "street",
                "street": "Mission"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["query_type"] == "street"

    def test_search_by_proximity_success(self, monkeypatch):
        """Test successful proximity search"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity",
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["query_type"] == "proximity"
        assert "search_coordinates" in data["metadata"]

    def test_search_by_proximity_with_status_filter(self, monkeypatch):
        """Test proximity search with status filter"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "status": "APPROVED"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["status_filter"] == "APPROVED"

    def test_search_with_custom_limit(self, monkeypatch):
        """Test search with custom limit"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "name",
                "applicant": "Taco",
                "limit": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["limit"] == 1
        assert len(data["data"]) <= 1

    def test_search_data_not_available(self, monkeypatch):
        """Test search when data is not available"""
        mock_data_loader = MagicMock()
        mock_data_loader.is_data_available.return_value = False
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "name",
                "applicant": "Taco"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Data not available" in data["detail"]

    def test_search_invalid_query_type(self):
        """Test search with invalid query type"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "invalid",
                "applicant": "Taco"
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_search_missing_required_fields_name(self):
        """Test name search with missing applicant"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "name"
                # Missing applicant
            }
        )
        
        assert response.status_code == 400

    def test_search_missing_required_fields_street(self):
        """Test street search with missing street"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "street"
                # Missing street
            }
        )
        
        assert response.status_code == 400

    def test_search_missing_required_fields_proximity(self):
        """Test proximity search with missing coordinates"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity"
                # Missing latitude/longitude
            }
        )
        
        assert response.status_code == 400

    def test_search_invalid_latitude_range(self):
        """Test search with invalid latitude range"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity",
                "latitude": 100.0,  # Invalid latitude
                "longitude": -122.4194
            }
        )
        
        assert response.status_code == 422

    def test_search_invalid_longitude_range(self):
        """Test search with invalid longitude range"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity",
                "latitude": 37.7749,
                "longitude": 200.0  # Invalid longitude
            }
        )
        
        assert response.status_code == 422

    def test_search_invalid_limit_range(self):
        """Test search with invalid limit range"""
        response = client.post(
            "/api/search",
            json={
                "query_type": "name",
                "applicant": "Taco",
                "limit": 0  # Invalid limit
            }
        )
        
        assert response.status_code == 422

    def test_search_proximity_default_limit(self, monkeypatch):
        """Test that proximity search defaults to limit 5"""
        mock_data_loader = MagicMock()
        mock_data_loader.get_data.return_value = self.sample_data
        mock_data_loader.is_data_available.return_value = True
        
        monkeypatch.setattr('app.api.search.data_loader', mock_data_loader)
        
        response = client.post(
            "/api/search",
            json={
                "query_type": "proximity",
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["limit"] == 5


class TestFrontendAPI:
    def test_frontend_index(self):
        """Test that frontend index page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert "SF Food Truck Finder" in response.text

    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        
        response = client.get("/static/styles.css")
        assert response.status_code == 200
