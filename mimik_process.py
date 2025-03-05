import json

# Load synthetic data
with open("./data/synthetic_data.json", "r") as f:
    data = json.load(f)

# Simulate mimik processing
processed_data = []
for entry in data:
    roads = entry["roads"]
    if entry["user_needs"] == "wheelchair":
        filtered_roads = [r for r in roads if r["accessible"]]
    else:
        filtered_roads = roads
    processed_entry = entry.copy()
    processed_entry["roads"] = filtered_roads
    processed_data.append(processed_entry)

# Save processed data
with open("./data/processed_data.json", "w") as f:
    json.dump(processed_data, f, indent=2)

print("Processed data saved")