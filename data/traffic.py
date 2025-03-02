from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import random

# Initialize Ollama with LLaMA 3.1
llm = Ollama(
                model="llama3.1", 
                base_url="http://localhost:11434"
                
                )  

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["num_entries"],
    template="""
    Generate {num_entries} synthetic datasets in JSON format for an AI evacuation planner during a wildfire in Los Angeles. Each dataset must include:
    - "user_location": a neighborhood in LA (e.g., "Downtown LA", "Pasadena", "Hollywood", "Santa Monica", "Westwood").
    - "fire_location": a road or area affected by fire (e.g., "Route 5", "Highway 101", "Main St", "Sunset Blvd", "Wilshire Blvd", or an LA neighborhood).
    - "roads": a list of 3 unique road options, each with:
      - "name": a road (e.g., "Route 5", "Highway 101", "Main St", "Sunset Blvd", "Wilshire Blvd").
      - "accessible": true or false.
      - "distance": integer in miles (1-10).
      - "safe_zone": a safe location (e.g., "Pasadena Community Center", "Shelter A", "Shelter B", "Santa Monica Pier").
    - "user_needs": a personal condition (e.g., "wheelchair", "none", "kids", "elderly").
    - "nearby_updates": a status message about one of the roads (e.g., "Route 5 congested", "Main St clear", "Sunset Blvd blocked").
    Ensure variety, realism, and valid JSON output for wildfire evacuation scenarios. Return the result as a JSON array.
    """
)

# Create the chain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Function to generate data in batches
def generate_synthetic_data(batch_size, num_batches):
    all_data = []
    for batch in range(num_batches):
        print(f"Generating batch {batch + 1}/{num_batches}...")
        try:
            # Generate batch
            response = chain.run(num_entries=batch_size)
            # Parse the JSON response
            batch_data = json.loads(response.strip())
            all_data.extend(batch_data)
        except Exception as e:
            print(f"Error in batch {batch + 1}: {e}")
            # Fallback: Generate dummy entry if LLM fails
            dummy_entry = {
                "user_location": "Downtown LA",
                "fire_location": "Highway 101",
                "roads": [
                    {"name": "Route 5", "accessible": True, "distance": 5, "safe_zone": "Pasadena Community Center"},
                    {"name": "Highway 101", "accessible": False, "distance": 2, "safe_zone": "Shelter A"},
                    {"name": "Main St", "accessible": False, "distance": 3, "safe_zone": "Shelter B"}
                ],
                "user_needs": "none",
                "nearby_updates": "Route 5 clear"
            }
            all_data.append(dummy_entry)
    return all_data

# Generate 1,200 entries (12 batches of 100)
batch_size = 100
num_batches = 12
synthetic_data = generate_synthetic_data(batch_size, num_batches)

# Save to file
with open("synthetic_data_1200.json", "w") as f:
    json.dump(synthetic_data, f, indent=2)

print(f"Generated {len(synthetic_data)} datasets. Saved to 'synthetic_data_1200.json'")