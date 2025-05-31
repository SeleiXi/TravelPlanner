import pandas as pd
from pandas import DataFrame
from typing import Optional
from utils.func import extract_before_parenthesis
import os


class Attractions:
    def __init__(self, path=None):
        if path is None:
            # Get the absolute path relative to this file's location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to TravelPlanner root, then to database/attractions
            path = os.path.join(current_dir, '..', '..', 'database', 'attractions', 'attractions.csv')
            path = os.path.abspath(path)
        self.path = path
        self.data = pd.read_csv(self.path).dropna()[['Name','Latitude','Longitude','Address','Phone','Website',"City"]]
        print("Attractions loaded.")

    def load_db(self):
        self.data = pd.read_csv(self.path)

    def run(self,
            city: str,
            ) -> DataFrame:
        """Search for Accommodations by city and date."""
        results = self.data[self.data["City"] == city]
        # the results should show the index
        results = results.reset_index(drop=True)
        if len(results) == 0:
            return "There is no attraction in this city."
        return results  
      
    def run_for_annotation(self,
            city: str,
            ) -> DataFrame:
        """Search for Accommodations by city and date."""
        results = self.data[self.data["City"] == extract_before_parenthesis(city)]
        # the results should show the index
        results = results.reset_index(drop=True)
        return results