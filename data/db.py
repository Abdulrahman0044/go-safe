import json
import chromadb
from langchain_ollama import OllamaEmbeddings

# Initialize ChromaDB client (local, persistent storage)
client = chromadb.PersistentClient(path="./evacuation_db")  # Saves to local directory
collection = client.get_or_create_collection("evacuation_data")

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings(model="llama3.1", base_url="http://localhost:11434")

# Load synthetic data
with open("synthetic_data.json", "r") as f:
    data = json.load(f)

# Prepare and store vectors
for i, entry in enumerate(data):
    text = f"{entry['user_location']} {entry['fire_location']} {entry['nearby_updates']}"
    embedding = embeddings.embed_query(text)
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        metadatas=[{
            "user_location": entry["user_location"],
            "fire_location": entry["fire_location"],
            "roads": json.dumps(entry["roads"]),
            "user_needs": entry["user_needs"],
            "nearby_updates": entry["nearby_updates"]
        }],
        documents=[text]  # Optional: store raw text for reference
    )

print(f"Stored {collection.count()} vectors in ChromaDB at './evacuation_db'")