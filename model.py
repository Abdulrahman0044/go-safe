import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EvacuationPlanner:
    def __init__(self, db_path=r"C:\Users\Abdulrahman A\go-safe\data\evacuation_db", cache_path=r"C:\Users\Abdulrahman A\go-safe\data\cached_plans.json", openai_key=None):
        # Initialize ChromaDB with specific path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection("evacuation_data")
        
        # Initialize embeddings (local with Ollama)
        self.embeddings = OllamaEmbeddings(model="llama3.1", base_url="http://localhost:11434")
        
        # Initialize OpenAI (optional, cloud-based)
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY", "")
        self.llm = OpenAI(api_key=self.openai_key, model="gpt-3.5-turbo-instruct") if self.openai_key else None
        
        # Load cached responses (offline fallback)
        try:
            with open(cache_path, "r") as f:
                self.cached_plans = json.load(f)
        except FileNotFoundError:
            self.cached_plans = {}
            print(f"Warning: {cache_path} not found. Offline mode will use basic fallback logic.")
        
        # RAG prompt
        self.prompt_template = PromptTemplate(
            input_variables=["context", "user_needs", "query"],
            template="""
            Given this context from an evacuation scenario:
            {context}
            And user needs: {user_needs}
            Provide a concise, personalized evacuation plan for: {query}
            Ensure the plan is clear, actionable, and tailored to the user's specific needs.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template) if self.llm else None

    def get_evacuation_plan(self, query, user_needs="none"):
        """Generate an evacuation plan based on query and user needs."""
        try:
            # Embed query locally
            query_embedding = self.embeddings.embed_query(query)
            
            # Query ChromaDB (local)
            result = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                include=["metadatas"]
            )
            
            # Extract context directly from metadata (no mimik processing)
            metadata = result["metadatas"][0][0]
            roads = json.loads(metadata["roads"])  # Use raw roads data
            if not roads:  # Handle empty roads case
                roads = [{"name": "unknown", "safe_zone": "nearest shelter"}]
            context = (
                f"User at {metadata['user_location']}, fire at {metadata['fire_location']}, "
                f"roads: {json.dumps(roads)}, updates: {metadata['nearby_updates']}"
            )
            
            # Generate plan
            if self.llm and os.getenv("ONLINE_MODE"):  # Check if online mode enabled
                plan = self.chain.run(context=context, user_needs=user_needs, query=query)
            else:  # Offline fallback
                key = f"{metadata['user_location']}_{metadata['fire_location']}_{user_needs}"
                plan = self.cached_plans.get(
                    key,
                    f"Evacuate via {roads[0]['name']} to {roads[0]['safe_zone']} based on local updates."
                )
            
            return plan.strip()
        
        except Exception as e:
            return f"Error generating plan: {str(e)}"

# Standalone usage (for testing)
if __name__ == "__main__":
    planner = EvacuationPlanner(
        db_path=r"C:\Users\Abdulrahman A\go-safe\data\evacuation_db",
        cache_path=r"C:\Users\Abdulrahman A\go-safe\data\cached_plans.json",
        openai_key="your-openai-api-key"  # Optional; omit for offline-only
    )
    query = "I need an evacuation route from Downtown LA with a fire on Highway 101"
    plan = planner.get_evacuation_plan(query, user_needs="wheelchair")
    print("Evacuation Plan:", plan)