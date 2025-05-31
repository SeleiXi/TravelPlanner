from pandas import DataFrame
import os

class Cities:
    def __init__(self, path=None) -> None:
        if path is None:
            # Get the absolute path relative to this file's location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to TravelPlanner root, then to database/background
            path = os.path.join(current_dir, '..', '..', 'database', 'background', 'citySet_with_states.txt')
            path = os.path.abspath(path)
        self.path = path
        self.load_data()
        print("Cities loaded.")

    def load_data(self):
        cityStateMapping = open(self.path, "r").read().strip().split("\n")
        self.data = {}
        for unit in cityStateMapping:
            city, state = unit.split("\t")
            if state not in self.data:
                self.data[state] = [city]
            else:
                self.data[state].append(city)
    
    def run(self, state) -> dict:
        if state not in self.data:
            return ValueError("Invalid State")
        else:
            return self.data[state]