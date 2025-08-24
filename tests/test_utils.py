import pytest
import pandas as pd
import numpy as np
from app.utils.search_utils import (
    apply_status_filter, search_by_name, search_by_street, search_by_proximity
)
from app.utils.mappers import convert_to_food_trucks, create_search_metadata
from app.utils.geo import haversine_distance
from app.models.food_truck import SearchType, StatusType


class TestGeoUtils:
    def test_haversine_distance_same_point(self):
        """Test haversine distance for same coordinates"""
        lat, lon = 37.7749, -122.4194
        distance = haversine_distance(lat, lon, lat, lon)
        assert distance == 0.0

    def test_haversine_distance_known_distance(self):
        """Test haversine distance for known coordinates"""
        # San Francisco to Oakland (approximately 13.4 km)
        sf_lat, sf_lon = 37.7749, -122.4194
        oak_lat, oak_lon = 37.8044, -122.2711
        distance = haversine_distance(sf_lat, sf_lon, oak_lat, oak_lon)
        assert 13.0 <= distance <= 14.0  # Allow some margin of error

    def test_haversine_distance_opposite_hemisphere(self):
        """Test haversine distance across hemispheres"""
        # San Francisco to Sydney (approximately 12,000 km)
        sf_lat, sf_lon = 37.7749, -122.4194
        syd_lat, syd_lon = -33.8688, 151.2093
        distance = haversine_distance(sf_lat, sf_lon, syd_lat, syd_lon)
        assert 11000 <= distance <= 13000  # Allow margin of error

    def test_haversine_distance_invalid_inputs(self):
        """Test haversine distance with invalid inputs"""
        with pytest.raises(TypeError):
            haversine_distance("invalid", -122.4194, 37.7749, -122.4194)


class TestSearchUtils:
    def setup_method(self):
        """Set up test data for each test method"""
        self.test_data = pd.DataFrame({
            'locationid': [1, 2, 3, 4],
            'Applicant': ['Taco Truck 1', 'Taco Truck 2', 'Burger Joint', 'Pizza Place'],
            'Address': ['123 Mission St', '456 Market St', '789 Castro St', '321 Valencia St'],
            'Status': ['APPROVED', 'REQUESTED', 'APPROVED', 'EXPIRED'],
            'Latitude': [37.7749, 37.7849, 37.7649, 37.7949],
            'Longitude': [-122.4194, -122.4094, -122.4294, -122.3994],
            'FoodItems': ['Tacos, Burritos', 'Tacos, Quesadillas', 'Burgers, Fries', 'Pizza, Pasta'],
            'FacilityType': ['Truck', 'Push Cart', 'Truck', 'Truck'],
            'permit': ['24MFF-00001', '24MFF-00002', '24MFF-00003', '24MFF-00004']
        })

    def test_apply_status_filter_with_status(self):
        """Test status filtering with specific status"""
        filtered = apply_status_filter(self.test_data, StatusType.APPROVED)
        assert len(filtered) == 2
        assert all(filtered['Status'] == 'APPROVED')

    def test_apply_status_filter_without_status(self):
        """Test status filtering without status (should return copy)"""
        filtered = apply_status_filter(self.test_data, None)
        assert len(filtered) == len(self.test_data)
        assert filtered is not self.test_data  # Should be a copy

    def test_apply_status_filter_returns_copy(self):
        """Test that status filtering returns a copy, not a view"""
        filtered = apply_status_filter(self.test_data, StatusType.APPROVED)
        # Modify the filtered data - should not affect original
        filtered.loc[filtered.index[0], 'Status'] = 'MODIFIED'
        assert self.test_data.loc[self.test_data.index[0], 'Status'] == 'APPROVED'

    def test_search_by_name_valid(self):
        """Test name search with valid input"""
        results = search_by_name(self.test_data, 'Taco')
        assert len(results) == 2
        assert all('Taco' in name for name in results['Applicant'])

    def test_search_by_name_case_insensitive(self):
        """Test that name search is case insensitive"""
        results = search_by_name(self.test_data, 'taco')
        assert len(results) == 2

    def test_search_by_name_with_status_filter(self):
        """Test name search with status filter"""
        results = search_by_name(self.test_data, 'Taco', StatusType.APPROVED)
        assert len(results) == 1
        assert results.iloc[0]['Status'] == 'APPROVED'

    def test_search_by_name_empty_result(self):
        """Test name search with no matches"""
        results = search_by_name(self.test_data, 'Nonexistent')
        assert len(results) == 0

    def test_search_by_name_missing_applicant(self):
        """Test name search with missing applicant"""
        with pytest.raises(ValueError, match="Applicant name required"):
            search_by_name(self.test_data, '')

    def test_search_by_street_valid(self):
        """Test street search with valid input"""
        results = search_by_street(self.test_data, 'Mission')
        assert len(results) == 1
        assert 'Mission' in results.iloc[0]['Address']

    def test_search_by_street_case_insensitive(self):
        """Test that street search is case insensitive"""
        results = search_by_street(self.test_data, 'mission')
        assert len(results) == 1

    def test_search_by_street_with_status_filter(self):
        """Test street search with status filter"""
        results = search_by_street(self.test_data, 'St', StatusType.APPROVED)
        assert len(results) == 2
        assert all(results['Status'] == 'APPROVED')

    def test_search_by_street_empty_result(self):
        """Test street search with no matches"""
        results = search_by_street(self.test_data, 'Nonexistent')
        assert len(results) == 0

    def test_search_by_street_missing_street(self):
        """Test street search with missing street"""
        with pytest.raises(ValueError, match="Street name required"):
            search_by_street(self.test_data, '')

    def test_search_by_proximity_valid(self):
        """Test proximity search with valid coordinates"""
        results = search_by_proximity(self.test_data, 37.7749, -122.4194)
        assert len(results) == 2  # Only APPROVED statuses by default
        # Should be sorted by distance (closest first)
        assert results.iloc[0]['Latitude'] == 37.7749
        assert results.iloc[0]['Longitude'] == -122.4194

    def test_search_by_proximity_with_status_filter(self):
        """Test proximity search with status filter"""
        results = search_by_proximity(self.test_data, 37.7749, -122.4194, StatusType.APPROVED)
        assert len(results) == 2
        assert all(results['Status'] == 'APPROVED')

    def test_search_by_proximity_missing_coordinates(self):
        """Test proximity search with missing coordinates"""
        with pytest.raises(ValueError, match="Latitude and longitude required"):
            search_by_proximity(self.test_data, None, -122.4194)

    def test_search_by_proximity_with_invalid_coordinates(self):
        """Test proximity search with invalid coordinates"""
        # Create data with some invalid coordinates
        invalid_data = self.test_data.copy()
        invalid_data.loc[0, 'Latitude'] = np.nan
        invalid_data.loc[1, 'Longitude'] = np.nan
        
        results = search_by_proximity(invalid_data, 37.7749, -122.4194)
        assert len(results) == 1  # Should filter out invalid coordinates and non-APPROVED statuses

    def test_search_by_proximity_distance_calculation(self):
        """Test that proximity search calculates distances correctly"""
        results = search_by_proximity(self.test_data, 37.7749, -122.4194)
        assert 'Distance' in results.columns
        # First result should have distance 0 (same coordinates)
        assert results.iloc[0]['Distance'] == 0.0


class TestMappers:
    def setup_method(self):
        """Set up test data for each test method"""
        self.test_data = pd.DataFrame({
            'locationid': [1, 2],
            'Applicant': ['Taco Truck 1', 'Taco Truck 2'],
            'Address': ['123 Mission St', '456 Market St'],
            'Status': ['APPROVED', 'REQUESTED'],
            'Latitude': [37.7749, 37.7849],
            'Longitude': [-122.4194, -122.4094],
            'FoodItems': ['Tacos, Burritos', 'Tacos, Quesadillas'],
            'FacilityType': ['Truck', 'Push Cart'],
            'permit': ['24MFF-00001', '24MFF-00002']
        })

    def test_convert_to_food_trucks(self):
        """Test conversion of DataFrame to FoodTruck objects"""
        food_trucks = convert_to_food_trucks(self.test_data)
        assert len(food_trucks) == 2
        assert food_trucks[0].applicant == 'Taco Truck 1'
        assert food_trucks[0].status == 'APPROVED'
        assert food_trucks[1].applicant == 'Taco Truck 2'
        assert food_trucks[1].status == 'REQUESTED'

    def test_convert_to_food_trucks_with_nan_values(self):
        """Test conversion with NaN values"""
        data_with_nan = self.test_data.copy()
        data_with_nan.loc[0, 'FoodItems'] = np.nan
        data_with_nan.loc[1, 'FacilityType'] = np.nan
        
        food_trucks = convert_to_food_trucks(data_with_nan)
        assert food_trucks[0].food_items is None
        assert food_trucks[1].facility_type is None

    def test_create_search_metadata_name_search(self):
        """Test metadata creation for name search"""
        metadata = create_search_metadata(
            SearchType.NAME, 
            StatusType.APPROVED, 
            10
        )
        assert metadata['query_type'] == 'name'
        assert metadata['status_filter'] == 'APPROVED'
        assert metadata['limit'] == 10
        assert 'search_coordinates' not in metadata

    def test_create_search_metadata_proximity_search(self):
        """Test metadata creation for proximity search"""
        metadata = create_search_metadata(
            SearchType.PROXIMITY,
            StatusType.APPROVED,
            5,
            latitude=37.7749,
            longitude=-122.4194
        )
        assert metadata['query_type'] == 'proximity'
        assert metadata['status_filter'] == 'APPROVED'
        assert metadata['limit'] == 5
        assert metadata['search_coordinates']['latitude'] == 37.7749
        assert metadata['search_coordinates']['longitude'] == -122.4194

    def test_create_search_metadata_no_status(self):
        """Test metadata creation without status filter"""
        metadata = create_search_metadata(SearchType.STREET, limit=15)
        assert metadata['query_type'] == 'street'
        assert metadata['status_filter'] is None
        assert metadata['limit'] == 15
