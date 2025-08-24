import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.dataloader.food_truck_loader import FoodTruckDataLoader


class TestFoodTruckDataLoader:
    def setup_method(self):
        """Set up test data for each test method"""
        self.loader = FoodTruckDataLoader()
        
        # Create sample test data
        self.sample_data = pd.DataFrame({
            'locationid': [1, 2, 3],
            'Applicant': ['Taco Truck 1', 'Taco Truck 2', 'Burger Joint'],
            'Status': ['APPROVED', 'REQUESTED', 'APPROVED'],
            'Address': ['123 Mission St', '456 Market St', '789 Castro St'],
            'Latitude': [37.7749, 37.7849, 37.7649],
            'Longitude': [-122.4194, -122.4094, -122.4294],
            'FoodItems': ['Tacos, Burritos', 'Tacos, Quesadillas', 'Burgers, Fries'],
            'FacilityType': ['Truck', 'Push Cart', 'Truck']
        })

    def test_initialization(self):
        """Test that loader initializes correctly"""
        assert self.loader._data is None
        assert self.loader._data_loaded is False
        assert self.loader._last_reload is None
        assert self.loader._reload_interval.total_seconds() == 60

    @patch('pandas.read_csv')
    def test_load_data_success(self, mock_read_csv):
        """Test successful data loading"""
        mock_read_csv.return_value = self.sample_data
        
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            result = self.loader.load_data()
            
        assert self.loader._data_loaded is True
        assert len(result) == 3
        assert result.equals(self.sample_data)
        mock_read_csv.assert_called_once()

    @patch('pandas.read_csv')
    def test_load_data_file_not_found(self, mock_read_csv):
        """Test data loading when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            result = self.loader.load_data()
        
        assert self.loader._data_loaded is False
        assert result.empty
        mock_read_csv.assert_not_called()

    @patch('pandas.read_csv')
    def test_load_data_exception_handling(self, mock_read_csv):
        """Test data loading with exception"""
        mock_read_csv.side_effect = Exception("Test error")
        
        with patch('os.path.exists', return_value=True):
            result = self.loader.load_data()
            
        assert self.loader._data_loaded is False
        assert result.empty
        assert isinstance(result, pd.DataFrame)

    def test_get_data_not_loaded(self):
        """Test getting data when not loaded"""
        self.loader._data_loaded = False
        self.loader._data = None
        with patch.object(self.loader, 'load_data') as mock_load:
            mock_load.return_value = self.sample_data
            # Mock the side effect to set the data
            def side_effect():
                self.loader._data = self.sample_data
                self.loader._data_loaded = True
                return self.sample_data
            mock_load.side_effect = side_effect
            result = self.loader.get_data()
            
        mock_load.assert_called_once()
        assert result.equals(self.sample_data)

    def test_get_data_already_loaded(self):
        """Test getting data when already loaded"""
        self.loader._data = self.sample_data
        self.loader._data_loaded = True
        
        with patch.object(self.loader, 'load_data') as mock_load:
            result = self.loader.get_data()
            
        mock_load.assert_not_called()
        assert result.equals(self.sample_data)

    def test_should_reload_never_reloaded(self):
        """Test reload check when never reloaded"""
        self.loader._last_reload = None
        assert self.loader.should_reload() is True

    def test_should_reload_recently_reloaded(self):
        """Test reload check when recently reloaded"""
        from datetime import datetime, timedelta
        self.loader._last_reload = datetime.now() - timedelta(seconds=30)
        assert self.loader.should_reload() is False

    def test_should_reload_old_reload(self):
        """Test reload check when reload is old"""
        from datetime import datetime, timedelta
        self.loader._last_reload = datetime.now() - timedelta(minutes=2)
        assert self.loader.should_reload() is True

    def test_is_data_available_not_loaded(self):
        """Test data availability when not loaded"""
        self.loader._data_loaded = False
        assert self.loader.is_data_available() is False

    def test_is_data_available_empty_data(self):
        """Test data availability when data is empty"""
        self.loader._data_loaded = True
        self.loader._data = pd.DataFrame()
        assert self.loader.is_data_available() is False

    def test_is_data_available_with_data(self):
        """Test data availability when data exists"""
        self.loader._data_loaded = True
        self.loader._data = self.sample_data
        assert self.loader.is_data_available() is True

    def test_get_dataframe(self):
        """Test getting DataFrame"""
        with patch.object(self.loader, 'get_data') as mock_get:
            mock_get.return_value = self.sample_data
            result = self.loader.get_dataframe()
            
        mock_get.assert_called_once()
        assert result.equals(self.sample_data)

    @patch('pandas.read_csv')
    def test_reload_data(self, mock_read_csv):
        """Test data reloading"""
        mock_read_csv.return_value = self.sample_data
        
        # Set initial state
        self.loader._data = pd.DataFrame({'old': ['data']})
        self.loader._data_loaded = True
        
        with patch('os.path.exists', return_value=True):
            result = self.loader.reload_data()
            
        assert self.loader._data_loaded is True  # load_data() sets this to True
        assert result.equals(self.sample_data)
        assert self.loader._last_reload is not None

    # Note: get_data_with_auto_reload method doesn't exist in the current implementation

    def test_data_loader_singleton(self):
        """Test that data_loader is a singleton instance"""
        from app.dataloader.food_truck_loader import data_loader
        assert isinstance(data_loader, FoodTruckDataLoader)
        assert data_loader is not None
