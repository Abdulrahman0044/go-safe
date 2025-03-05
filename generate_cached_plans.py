import json

# Load processed data
try:
    with open("./data/processed_data.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("processed_data.json not found. Run mimik processing step first.")

# Generate cached plans
cached_plans = {}
for entry in data:
    key = f"{entry['user_location']}_{entry['fire_location']}_{entry['user_needs']}"
    roads = entry["roads"]
    
    # Handle empty roads list
    if not roads:
        plan = "No safe routes available. Shelter in place and await rescue."
    else:
        # Pick the first safe road based on user needs
        safe_road = next(
            (r for r in roads if entry["user_needs"] != "wheelchair" or r["accessible"]),
            roads[0]  # Fallback to first road if no match
        )
        plan = f"Evacuate via {safe_road['name']} to {safe_road['safe_zone']}."
    
    cached_plans[key] = plan

# Save to file
cache_path = "./data/cached_plans.json"
with open(cache_path, "w") as f:
    json.dump(cached_plans, f, indent=2)

print(f"Generated {len(cached_plans)} cached plans at {cache_path}")