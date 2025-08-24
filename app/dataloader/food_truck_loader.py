import pandas as pd
import os
import asyncio
from datetime import datetime, timedelta

class FoodTruckDataLoader:
    def __init__(self):
        self._data = None
        self._data_loaded = False
        self._last_reload = None
        self._reload_interval = timedelta(minutes=1)  # Reload every 1 minute
    
    def load_data(self):
        """Load the CSV data into memory if not already loaded"""
        if not self._data_loaded:
            try:
                csv_path = 'datastore/Mobile_Food_Facility_Permit_20250822.csv'
                if not os.path.exists(csv_path):
                    raise FileNotFoundError(f"CSV file not found at {csv_path}")
                
                self._data = pd.read_csv(csv_path)
                
                self._data_loaded = True
                print(f"Data loaded successfully. {len(self._data)} records loaded.")
                
            except Exception as e:
                print(f"Error loading data: {e}")
                self._data = pd.DataFrame()
                self._data_loaded = False
        
        return self._data
    
    def get_data(self):
        """Get the loaded data"""
        if not self._data_loaded:
            self.load_data()
        return self._data
    
    def should_reload(self):
        """Check if data should be reloaded based on time interval"""
        if self._last_reload is None:
            return True
        return datetime.now() - self._last_reload >= self._reload_interval
    
    def is_data_available(self):
        """Check if data is available"""
        return self._data_loaded and not self._data.empty
    
    def get_dataframe(self):
        """Get the pandas DataFrame"""
        return self.get_data()
    
    def reload_data(self):
        """Force reload the data (useful for testing or data updates)"""
        self._data = None
        self._data_loaded = False
        result = self.load_data()
        self._last_reload = datetime.now()
        return result

# Global instance
data_loader = FoodTruckDataLoader()
