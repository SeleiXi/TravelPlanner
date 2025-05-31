import pandas as pd
from pandas import DataFrame
from typing import Optional
from utils.func import extract_before_parenthesis
import os

class Restaurants:
    def __init__(self, path=None):
        if path is None:
            # Get the absolute path relative to this file's location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to TravelPlanner root, then to database/restaurants
            path = os.path.join(current_dir, '..', '..', 'database', 'restaurants', 'clean_restaurant_2022.csv')
            path = os.path.abspath(path)
        self.path = path
        self.data = pd.read_csv(self.path).dropna()[['Name','Average Cost','Cuisines','Aggregate Rating','City']]
        print("Restaurants loaded.")

    def load_db(self):
        self.data = pd.read_csv(self.path).dropna()

    def run(self,
            city: str,
            ) -> DataFrame:
        """Search for restaurant ."""
        results = self.data[self.data["City"] == city]
        # results = results[results["date"] == date]
        # if price_order == "asc":
        #     results = results.sort_values(by=["Average Cost"], ascending=True)
        # elif price_order == "desc": 
        #     results = results.sort_values(by=["Average Cost"], ascending=False)

        # if rating_order == "asc":
        #     results = results.sort_values(by=["Aggregate Rating"], ascending=True)
        # elif rating_order == "desc":
        #     results = results.sort_values(by=["Aggregate Rating"], ascending=False)
        if len(results) == 0:
            return "There is no restaurant in this city."
        return results

    def run_for_annotation(self,
            city: str,
            ) -> DataFrame:
        """Search for restaurant ."""
        results = self.data[self.data["City"] == extract_before_parenthesis(city)]
        # results = results[results["date"] == date]
        # if price_order == "asc":
        #     results = results.sort_values(by=["Average Cost"], ascending=True)
        # elif price_order == "desc":
        #     results = results.sort_values(by=["Average Cost"], ascending=False)

        # if rating_order == "asc":
        #     results = results.sort_values(by=["Aggregate Rating"], ascending=True)
        # elif rating_order == "desc":
        #     results = results.sort_values(by=["Aggregate Rating"], ascending=False)

        return results