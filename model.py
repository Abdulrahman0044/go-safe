import chromadb
from langchain_community.embeddings import OllamaEmbeddings  # Still used for local embedding
from langchain_openai import OpenAI  # OpenAI for generation
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./evacuation_db")
collection = client.get_collection("evacuation_data")

# Initialize embeddings (local with Ollama)
embeddings = OllamaEmbeddings(model="llama3.1", base_url="http://localhost:11434")

# Initialize OpenAI (cloud-based generation)
openai_llm = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo-instruct"  # Or "gpt-4" if available; adjust per your access
)

# RAG prompt
prompt_template = PromptTemplate(
    input_variables=["context", "user_needs", "query"],
    template="""
    Given this context from an evacuation scenario:
    {context}
    And user needs: {user_needs}
    Provide a concise, personalized evacuation plan for: {query}
    Ensure the plan is clear, actionable, and tailored to the user's specific needs.
    """
)
chain = LLMChain(llm=openai_llm, prompt=prompt_template)

# Query function
def get_evacuation_plan(query, user_needs="none"):
    # Embed the query locally
    query_embedding = embeddings.embed_query(query)
    
    # Query ChromaDB (local)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        include=["metadatas"]
    )
    
    # Extract context from local store
    metadata = result["metadatas"][0][0]
    context = f"User at {metadata['user_location']}, fire at {metadata['fire_location']}, roads: {metadata['roads']}, updates: {metadata['nearby_updates']}"
    
    # Generate plan with OpenAI
    plan = chain.run(context=context, user_needs=user_needs, query=query)
    return plan.strip()

# Test
user_input = "I need an evacuation route from Downtown LA with a fire on Highway 101"
plan = get_evacuation_plan(user_input, user_needs="wheelchair")
print("Evacuation Plan:", plan)