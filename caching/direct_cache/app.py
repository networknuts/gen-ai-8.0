import redis
from openai import OpenAI 
from dotenv import load_dotenv
import hashlib

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# STEP 1: CREATE A HASHING STRATEGY
def convert_hash(prompt: str):
    normalized = prompt.strip().lower()
    hashed = hashlib.sha256(normalized.encode()).hexdigest()
    return f"cache:{hashed}"

# STEP 2: GET THE LLM RESPONSE
def ask_llm(prompt: str):
    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt
    )
    return response.output_text

# STEP 3: MAIN LOGIC

def get_response(prompt):
    key = convert_hash(prompt)
    cached_output = redis_client.get(key)
    if cached_output:
        print("FOUND RESPONSE IN CACHE")
        return cached_output
    else:
        print("INVOKING LLM CALL")
        answer = ask_llm(prompt)
        # IF ANSWER IS FOUND, GIVE ANSWER TO CUSTOMER AND SAVE ANSWER TO REDIS AS WELL
        redis_client.set(key,answer)
        return answer 

query = input("Human Query: ")
print("\nAI RESPONSE\n")
print(get_response(query))