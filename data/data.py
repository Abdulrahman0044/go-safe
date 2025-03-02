import random
import json

# Define possible values
locations = ["Downtown LA", "Pasadena", "Hollywood", "Santa Monica", "Westwood"]
roads_list = ["Route 5", "Highway 101", "Main St", "Sunset Blvd", "Wilshire Blvd"]
safe_zones = ["Pasadena Community Center", "Shelter A", "Shelter B", "Santa Monica Pier"]
user_needs_options = ["wheelchair", "none", "kids", "elderly"]
updates_options = ["{road} congested", "{road} clear", "{road} blocked"]

# Generate 1200 datasets
data = []
for _ in range(1200):
    # Random road details
    road_options = random.sample(roads_list, 3)  # Pick 3 unique roads
    roads = [
        {
            "name": road,
            "accessible": random.choice([True, False]),
            "distance": random.randint(1, 10),
            "safe_zone": random.choice(safe_zones)
        }
        for road in road_options
    ]
    
    # Random fire location (sometimes a road, sometimes an area)
    fire_loc = random.choice(roads_list + locations)
    
    # Ensure user location differs from fire location
    user_loc = random.choice([loc for loc in locations if loc != fire_loc])
    
    # Random user needs
    user_needs = random.choice(user_needs_options)
    
    # Random nearby update
    update_road = random.choice(road_options)
    nearby_updates = random.choice(updates_options).format(road=update_road)
    
    # Compile dataset
    entry = {
        "user_location": user_loc,
        "fire_location": fire_loc,
        "roads": roads,
        "user_needs": user_needs,
        "nearby_updates": nearby_updates
    }
    data.append(entry)

# Save to file
with open("synthetic_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Generated 1200 synthetic datasets. Saved to 'synthetic_data.json'")