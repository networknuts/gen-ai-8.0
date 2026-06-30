import redis
from openai import OpenAI 
from dotenv import load_dotenv
import hashlib 
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid 

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)
qdrant = QdrantClient(url="http://localhost:6333")

COLLECTION = "cache"

# HASHING STRATEGY
def convert_key(prompt: str):
    normalized = prompt.strip().lower()
    hashed = hashlib.sha256(normalized.encode()).hexdigest()
    return f"cache:{hashed}"

# LLM RESPONSE
def ask_llm(prompt: str):
    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt
    )
    return response.output_text

# EMBEDDING MODEL STRATEGY
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# INITIALIZE THE VECTOR DATABASE
def init_collection():
    try:
        qdrant.get_collection(COLLECTION)
    except:
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE)
        )

# SEARCH THE COLLECTION FOR SEMANTIC RESULT
def search_cache(embedding):
    result = qdrant.query_points(
        collection_name=COLLECTION,
        query=embedding,
        limit=1
    )
    if len(result.points) == 0:
        return None
    point = result.points[0]
    if point.score > 0.9:
        return point.payload["answer"]
    return None 

# SAVE NEW ANSWER TO VECTOR DATABASE
def save_cache(prompt,embedding,answer):
    qdrant.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "prompt": prompt,
                    "answer": answer
                }
            )
        ]
    )

# MAIN LOGIC

def get_answer(prompt):
    key = convert_key(prompt)
    cached_output = redis_client.get(key)
    if cached_output:
        print("FOUND RESPONSE IN DIRECT CACHE")
        return cached_output
    else:
        emb = get_embedding(prompt)
        init_collection()
        semantic = search_cache(emb)
        if semantic:
            print("FOUND RESPONSE IN SEMANTIC CACHE")
            redis_client.set(key,semantic)
            return semantic
        else:
            print("INVOKING LLM CALL")
            answer = ask_llm(prompt)
            #SAVE ANSWER TO DIRECT CACHE
            redis_client.set(key,answer)
            #SAVE ANSWER TO SEMANTIC CACHE
            save_cache(prompt,emb,answer)
            return answer

query = input("Human Query: ")
print("AI RESPONSE\n")
print(get_answer(query))