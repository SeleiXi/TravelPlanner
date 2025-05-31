import pandas as pd
from pandas import DataFrame
from typing import Optional
from utils.func import extract_before_parenthesis
import os


class Accommodations:
    def __init__(self, path=None):
        if path is None:
            # Get the absolute path relative to this file's location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to TravelPlanner root, then to database/accommodations
            path = os.path.join(current_dir, '..', '..', 'database', 'accommodations', 'clean_accommodations_2022.csv')
            path = os.path.abspath(path)
        self.path = path
        self.data = pd.read_csv(self.path).dropna()[['NAME','price','room type', 'house_rules', 'minimum nights', 'maximum occupancy', 'review rate number', 'city']]
        print("Accommodations loaded.")

    def load_db(self):
        self.data = pd.read_csv(self.path).dropna()

    def run(self,
            city: str,
            ) -> DataFrame:
        """Search for accommodations by city."""
        results = self.data[self.data["city"] == city]
        if len(results) == 0:
            return "There is no attraction in this city."
        
        return results
    
    def run_for_annotation(self,
            city: str,
            ) -> DataFrame:
        """Search for accommodations by city."""
        results = self.data[self.data["city"] == extract_before_parenthesis(city)]
        return results