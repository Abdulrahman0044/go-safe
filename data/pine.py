import json
import os
import torch
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM

load_dotenv()

# Initialize Pinecone
pinecone_api_key=os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

# Create or connect to an index
index_name = "evacuation-planner"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=4096,  
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)
index = pc.Index(index_name)

# Load synthetic data
with open("synthetic_data.json", "r") as f:
    data = json.load(f)

# Initialize embedding model
embeddings = OllamaEmbeddings(
    model="llama3.1",  # Using llama3.1 model
    base_url="http://localhost:11434",  # Ollama server URL
)

# Prepare data for upsert
vectors = []
for i, entry in enumerate(data):
    # Combine relevant fields into a single text string for embedding
    text = f"{entry['user_location']} {entry['fire_location']} {entry['nearby_updates']}"
    embedding = embeddings.embed_query(text)
    # Use metadata to store original data
    metadata = {
        "user_location": entry["user_location"],
        "fire_location": entry["fire_location"],
        "roads": json.dumps(entry["roads"]),  # Store as JSON string
        "user_needs": entry["user_needs"],
        "nearby_updates": entry["nearby_updates"]
    }
    vectors.append((str(i), embedding, metadata))

# Upsert vectors into Pinecone
index.upsert(vectors=vectors)
print(f"Upserted {len(vectors)} vectors into Pinecone index '{index_name}'")