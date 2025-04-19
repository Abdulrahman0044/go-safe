import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EvacuationPlanner:
    def __init__(self, db_path=r"C:\Users\Abdulrahman A\go-safe\data\evacuation_db", cache_path=r"C:\Users\Abdulrahman A\go-safe\data\cached_plans.json", groq_api_key=None):
        print(f"DEBUG: Initializing with db_path: {db_path}")
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_collection("evacuation_data")
            print("DEBUG: ChromaDB initialized")
        except Exception as e:
            print(f"DEBUG: ChromaDB init failed: {str(e)}")
            self.client = None
            self.collection = None
        self.embeddings = OllamaEmbeddings(model="llama3.1", base_url="http://localhost:11434")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self.llm = ChatGroq(api_key=self.groq_api_key, model="mistral-saba-24b") if self.groq_api_key else None
        try:
            with open(cache_path, "r") as f:
                self.cached_plans = json.load(f)
        except FileNotFoundError:
            self.cached_plans = {}
            print(f"Warning: {cache_path} not found.")
        self.prompt_template = PromptTemplate(
            input_variables=["context", "user_needs", "query"],
            template="""
            Given this context from an evacuation scenario:
            {context}
            And user needs: {user_needs}
            Respond to this query: {query}
            Provide a clear, step-by-step evacuation plan as a numbered list. 
            Begin with "1. Start at [user location]" and end with "X. Proceed to [safe zone with specific name, e.g., Pasadena Community Center]". 
            Include specific roads or directions (e.g., "2. Take [road] north") based on available roads and updates.
            Tailor the route to the user's needs (e.g., wheelchair access).
            Avoid vague terms like 'nearest shelter'—use a real, mappable location.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template) if self.llm else None

    def get_evacuation_plan(self, query, user_needs="none"):
        try:
            print(f"DEBUG: Query: {query}")
            user_location = "unknown location"
            fire_location = "unknown fire"
            if "from" in query.lower():
                user_location = query.lower().split("from")[1].split("with")[0].strip()
            if "fire on" in query.lower():
                fire_location = query.lower().split("fire on")[1].strip()

            if self.collection:
                query_embedding = self.embeddings.embed_query(query)
                result = self.collection.query(query_embeddings=[query_embedding], n_results=1, include=["metadatas"])
                print(f"DEBUG: Query result: {result}")
                if not result["metadatas"] or not result["metadatas"][0]:
                    print("DEBUG: No metadata found, using fallback")
                    metadata = {
                        "user_location": user_location,
                        "fire_location": fire_location,
                        "roads": json.dumps([{"name": "Route 5", "safe_zone": "Pasadena Community Center"}]),
                        "nearby_updates": "no updates"
                    }
                else:
                    metadata = result["metadatas"][0][0]
            else:
                print("DEBUG: No ChromaDB collection, using fallback")
                metadata = {
                    "user_location": user_location,
                    "fire_location": fire_location,
                    "roads": json.dumps([{"name": "Route 5", "safe_zone": "Pasadena Community Center"}]),
                    "nearby_updates": "no updates"
                }

            roads = json.loads(metadata["roads"])
            if not roads:
                roads = [{"name": "Route 5", "safe_zone": "Pasadena Community Center"}]
            context = (
                f"User at {metadata['user_location']}, fire at {metadata['fire_location']}, "
                f"roads: {json.dumps(roads)}, updates: {metadata.get('nearby_updates', 'no updates')}"
            )
            print(f"DEBUG: Context: {context}")

            if self.llm and os.getenv("ONLINE_MODE"):
                plan = self.chain.run(context=context, user_needs=user_needs, query=query)
            else:
                key = f"{metadata['user_location']}_{metadata['fire_location']}_{user_needs}"
                plan = self.cached_plans.get(
                    key, self._format_fallback_plan(roads, metadata["user_location"], metadata["fire_location"])
                )
            print(f"DEBUG: Raw plan:\n{plan}")
            start, waypoints, destination = self._parse_plan(plan)
            if not start:
                start = metadata["user_location"]
            if not destination:
                destination = roads[0]["safe_zone"]
            print(f"DEBUG: Parsed - start: {start}, waypoints: {waypoints}, destination: {destination}")
            return {
                "plan": plan.strip(),
                "start": start,
                "waypoints": waypoints,
                "destination": destination
            }
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            return {"plan": f"Error generating plan: {str(e)}", "start": None, "waypoints": [], "destination": None}

    def _format_fallback_plan(self, roads, user_location, fire_location):
        return (
            f"1. Start at {user_location}.\n"
            f"2. Avoid {fire_location} by taking {roads[0]['name']}.\n"
            f"3. Proceed to {roads[0]['safe_zone']}."
        )

    def _parse_plan(self, plan):
        lines = plan.split("\n")
        start = None
        waypoints = []
        destination = None
        for i, line in enumerate(lines):
            line = line.strip()
            if i == 0 or "start" in line.lower() or "begin" in line.lower():
                parts = line.split('.', 1)
                if len(parts) > 1:
                    start = parts[1].strip().replace("Start at", "").replace("Begin at", "").rstrip(".")
            elif "arrive" in line.lower() or "proceed to" in line.lower() or "reach" in line.lower() or i == len(lines) - 1:
                parts = line.split('.', 1)
                if len(parts) > 1:
                    destination = parts[1].strip()
                    for prefix in ["Arrive at", "Proceed to", "Reach"]:
                        destination = destination.split(prefix)[-1].strip().rstrip(".")
            else:
                parts = line.split('.', 1)
                if len(parts) > 1:
                    waypoint = parts[1].strip()
                    # Extract road name after "taking" if present
                    if "by taking" in waypoint:
                        waypoint = waypoint.split("by taking")[-1].strip()
                    elif "Take" in waypoint:
                        waypoint = waypoint.replace("Take", "").strip()
                    waypoints.append(waypoint)
        return start, waypoints, destination