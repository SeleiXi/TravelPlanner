"""
Script to convert JSONL reference data to CSV files for TravelPlanner database

Usage:
    python jsonl_to_csv_converter.py --input test_ref_info.jsonl
    python jsonl_to_csv_converter.py --input test_ref_info.jsonl --output-dir custom_output/
"""

import json
import argparse
import csv
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of parsed JSON objects"""
    data = []
    
    print(f"Loading JSONL file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    print(f"Loaded {len(data)} entries from JSONL")
    return data


def extract_category_data(jsonl_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Extract and organize data by category"""
    category_data = defaultdict(list)
    
    for entry in jsonl_data:
        for key, value in entry.items():
            # Handle the standard "Category in City" pattern
            if " in " in key and isinstance(value, list) and value:
                category, city = key.split(" in ", 1)
                
                # Add city information to each item if not present
                for item in value:
                    if isinstance(item, dict):
                        # Add city field if not present
                        if "City" not in item and "city" not in item:
                            item["City"] = city
                        category_data[category].append(item)
            
            # Handle flight data: "Flight from [Origin] to [Destination] on [Date]"
            elif key.startswith("Flight from ") and isinstance(value, list) and value:
                # Extract flight data
                for item in value:
                    if isinstance(item, dict):
                        category_data["Flights"].append(item)
            
            # Handle distance matrix data: "Self-driving from [Origin] to [Destination]"
            elif key.startswith("Self-driving from ") and isinstance(value, str):
                # Parse the string format: "self-driving, from [origin] to [destination], duration: X, distance: Y, cost: Z"
                try:
                    parts = value.split(", ")
                    if len(parts) >= 4:
                        # Extract origin and destination from the key
                        route_part = key.replace("Self-driving from ", "")
                        if " to " in route_part:
                            origin, destination = route_part.split(" to ", 1)
                            
                            # Parse duration, distance, cost from the value string
                            duration = ""
                            distance = ""
                            cost = ""
                            
                            for part in parts:
                                if part.startswith("duration: "):
                                    duration = part.replace("duration: ", "")
                                elif part.startswith("distance: "):
                                    distance = part.replace("distance: ", "")
                                elif part.startswith("cost: "):
                                    cost = part.replace("cost: ", "")
                            
                            distance_item = {
                                "origin": origin,
                                "destination": destination,
                                "duration": duration,
                                "distance": distance,
                                "cost": cost
                            }
                            category_data["GoogleDistanceMatrix"].append(distance_item)
                except Exception as e:
                    print(f"Error parsing distance data for key '{key}': {e}")
                    continue
            
            # Handle taxi data as additional distance matrix entries
            elif key.startswith("Taxi from ") and isinstance(value, str):
                try:
                    parts = value.split(", ")
                    if len(parts) >= 4:
                        # Extract origin and destination from the key
                        route_part = key.replace("Taxi from ", "")
                        if " to " in route_part:
                            origin, destination = route_part.split(" to ", 1)
                            
                            # Parse duration, distance, cost from the value string
                            duration = ""
                            distance = ""
                            cost = ""
                            
                            for part in parts:
                                if part.startswith("duration: "):
                                    duration = part.replace("duration: ", "")
                                elif part.startswith("distance: "):
                                    distance = part.replace("distance: ", "")
                                elif part.startswith("cost: "):
                                    cost = part.replace("cost: ", "")
                            
                            distance_item = {
                                "origin": origin,
                                "destination": destination,
                                "duration": duration,
                                "distance": distance,
                                "cost": cost,
                                "mode": "taxi"
                            }
                            category_data["GoogleDistanceMatrix"].append(distance_item)
                except Exception as e:
                    print(f"Error parsing taxi data for key '{key}': {e}")
                    continue
    
    return dict(category_data)


def write_attractions_csv(data: List[Dict[str, Any]], output_file: str):
    """Write attractions data to CSV"""
    print(f"Writing {len(data)} attractions to {output_file}")
    
    # Define expected columns
    columns = ["Name", "Latitude", "Longitude", "Address", "Phone", "Website", "City"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for item in data:
            # Create a clean row
            row = {}
            for col in columns:
                row[col] = item.get(col, "Unknown")
            writer.writerow(row)


def write_restaurants_csv(data: List[Dict[str, Any]], output_file: str):
    """Write restaurants data to CSV"""
    print(f"Writing {len(data)} restaurants to {output_file}")
    
    # Define expected columns
    columns = ["Name", "Average Cost", "Cuisines", "Aggregate Rating", "City"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for item in data:
            # Create a clean row
            row = {}
            for col in columns:
                value = item.get(col, "Unknown")
                # Handle numeric fields
                if col == "Average Cost" and isinstance(value, (int, float)):
                    row[col] = value
                elif col == "Aggregate Rating" and isinstance(value, (int, float)):
                    row[col] = value
                else:
                    row[col] = str(value) if value is not None else "Unknown"
            writer.writerow(row)


def write_accommodations_csv(data: List[Dict[str, Any]], output_file: str):
    """Write accommodations data to CSV"""
    print(f"Writing {len(data)} accommodations to {output_file}")
    
    # Define expected columns (note: NAME instead of Name for accommodations)
    columns = ["NAME", "price", "room type", "house_rules", "minimum nights", "maximum occupancy", "review rate number", "city"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for item in data:
            # Create a clean row
            row = {}
            for col in columns:
                if col == "city":
                    # Handle both "City" and "city" variations
                    value = item.get("City", item.get("city", "Unknown"))
                else:
                    value = item.get(col, "Unknown")
                
                # Handle numeric fields
                if col in ["price", "minimum nights", "maximum occupancy", "review rate number"]:
                    if isinstance(value, (int, float)):
                        row[col] = value
                    else:
                        try:
                            row[col] = float(value) if value != "Unknown" else 0.0
                        except (ValueError, TypeError):
                            row[col] = 0.0
                else:
                    row[col] = str(value) if value is not None else "Unknown"
            writer.writerow(row)


def write_flights_csv(data: List[Dict[str, Any]], output_file: str):
    """Write flights data to CSV"""
    print(f"Writing {len(data)} flights to {output_file}")
    
    # Define expected columns for flights
    columns = ["Flight Number", "Price", "DepTime", "ArrTime", "ActualElapsedTime", "FlightDate", "OriginCityName", "DestCityName", "Distance"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for item in data:
            # Create a clean row
            row = {}
            for col in columns:
                value = item.get(col, "Unknown")
                # Handle numeric fields
                if col in ["Price", "Distance"]:
                    if isinstance(value, (int, float)):
                        row[col] = value
                    else:
                        try:
                            row[col] = float(value) if value != "Unknown" else 0.0
                        except (ValueError, TypeError):
                            row[col] = 0.0
                else:
                    row[col] = str(value) if value is not None else "Unknown"
            writer.writerow(row)


def write_distance_matrix_csv(data: List[Dict[str, Any]], output_file: str):
    """Write distance matrix data to CSV"""
    print(f"Writing {len(data)} distance entries to {output_file}")
    
    # Define expected columns for distance matrix
    columns = ["origin", "destination", "distance", "duration"]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for item in data:
            # Create a clean row
            row = {}
            for col in columns:
                value = item.get(col, "Unknown")
                row[col] = str(value) if value is not None else "Unknown"
            writer.writerow(row)


def get_unique_cities(category_data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """Extract unique cities from all categories"""
    cities = set()
    
    for category, items in category_data.items():
        for item in items:
            city = item.get("City", item.get("city"))
            if city and city != "Unknown":
                cities.add(city)
    
    return sorted(list(cities))


def create_directory_structure(output_dir: str):
    """Create the necessary directory structure"""
    directories = [
        "attractions",
        "restaurants", 
        "accommodations",
        "flights",
        "googleDistanceMatrix",
        "background"
    ]
    
    for directory in directories:
        Path(os.path.join(output_dir, directory)).mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSONL reference data to CSV files for TravelPlanner database"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default="test_ref_info.jsonl",
        help="Input JSONL file (default: test_ref_info.jsonl)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for CSV files (default: current directory)"
    )
    
    parser.add_argument(
        "--cities-limit",
        type=int,
        default=None,
        help="Limit number of cities to process (for testing)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        return
    
    print(f"Input file: {args.input}")
    print(f"Output directory: {args.output_dir}")
    
    # Create directory structure
    create_directory_structure(args.output_dir)
    
    # Load JSONL data
    jsonl_data = load_jsonl(args.input)
    
    if not jsonl_data:
        print("No data found in JSONL file")
        return
    
    # Extract category data
    category_data = extract_category_data(jsonl_data)
    
    print(f"Found categories: {list(category_data.keys())}")
    for category, items in category_data.items():
        print(f"  {category}: {len(items)} items")
    
    # Get unique cities
    cities = get_unique_cities(category_data)
    print(f"Found {len(cities)} unique cities")
    
    if args.cities_limit:
        cities = cities[:args.cities_limit]
        print(f"Limited to {len(cities)} cities for processing")
    
    # Write CSV files for each category
    if "Attractions" in category_data:
        output_file = os.path.join(args.output_dir, "attractions", "attractions.csv")
        write_attractions_csv(category_data["Attractions"], output_file)
    
    if "Restaurants" in category_data:
        output_file = os.path.join(args.output_dir, "restaurants", "clean_restaurant_2022.csv")
        write_restaurants_csv(category_data["Restaurants"], output_file)
    
    if "Accommodations" in category_data:
        output_file = os.path.join(args.output_dir, "accommodations", "clean_accommodations_2022.csv")
        write_accommodations_csv(category_data["Accommodations"], output_file)
    
    if "Flights" in category_data:
        output_file = os.path.join(args.output_dir, "flights", "clean_Flights_2022.csv")
        write_flights_csv(category_data["Flights"], output_file)
    
    if "GoogleDistanceMatrix" in category_data:
        output_file = os.path.join(args.output_dir, "googleDistanceMatrix", "distance.csv")
        write_distance_matrix_csv(category_data["GoogleDistanceMatrix"], output_file)
    
    # Create cities list file
    cities_file = os.path.join(args.output_dir, "background", "citySet.txt")
    with open(cities_file, 'w', encoding='utf-8') as f:
        for city in cities:
            f.write(f"{city}\n")
    print(f"Created cities file: {cities_file} with {len(cities)} cities")
    
    print("CSV conversion completed successfully!")


if __name__ == "__main__":
    main() 