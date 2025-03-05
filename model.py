import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json
from dotenv import load_dotenv

load_dotenv()
openai_key = os.environ.get("OPENAI_API_KEY")

class EvacuationPlanner:
    def __init__(self, db_path="./data/evacuation_db", cache_path="./data/cached_plans.json", openai_key=None):
        # Initialize ChromaDB with specific path (raw string to handle backslashes)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection("evacuation_data")
        
        # Initialize embeddings (local with Ollama)
        self.embeddings = OllamaEmbeddings(model="llama3.1", base_url="http://localhost:11434")
        
        # Initialize OpenAI (optional, cloud-based)
        self.openai_key = openai_key or os.environ.get("OPENAI_API_KEY", "")
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
        self.chain = LLMChain(llm=self.llm, prompt=prompt_template) if self.llm else None

    def process_with_mimik(self, metadata):
        """Placeholder for mimik edge processing."""
        # Hypothetical mimik integration; adjust per SDK
        try:
            mimik_token = os.environ.get("MIMIK_TOKEN")
            if not mimik_token:
                raise ValueError("MIMIK_TOKEN not found in .env file")
            edge_client = EdgeClient(access_token=mimik_token)
            roads = json.loads(metadata["roads"])
            user_needs = metadata["user_needs"]
            filtered_roads = [r for r in roads if user_needs != "wheelchair" or r["accessible"]]
            edge_client.deploy_microservice(
                service_name="evacuation_filter",
                data={"roads": filtered_roads}
            )
            return filtered_roads
        except ImportError:
            # Fallback if mimik SDK unavailable
            roads = json.loads(metadata["roads"])
            user_needs = metadata["user_needs"]
            return [r for r in roads if user_needs != "wheelchair" or r["accessible"]]

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
            
            # Extract context
            metadata = result["metadatas"][0][0]
            roads = self.process_with_mimik(metadata)  # mimik edge processing
            context = (
                f"User at {metadata['user_location']}, fire at {metadata['fire_location']}, "
                f"roads: {json.dumps(roads)}, updates: {metadata['nearby_updates']}"
            )
            
            # Generate plan
            if self.llm and os.environ.get("ONLINE_MODE"):  # Check if online mode enabled
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
## Comment out for actual deployment
if __name__ == "__main__":
    planner = EvacuationPlanner(
        db_path="./data/evacuation_db",
        cache_path="./data/cached_plans.json",
        openai_key=openai_key # Optional; omit for offline-only
    )
    query = "I need an evacuation route from Downtown LA with a fire on Highway 101"
    plan = planner.get_evacuation_plan(query, user_needs="wheelchair")
    print("Evacuation Plan:", plan)