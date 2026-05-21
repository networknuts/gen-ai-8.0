import requests 
import os 
from dotenv import load_dotenv
import json 

# ASK USER FOR INPUT
query = input("Human Query: ")

# LOAD THE INSTRUCTIONS FILE
f = open("instructions.txt","r")
SYSTEM_INSTRUCTIONS = f.read()
f.close()

# LOAD THE .ENV FILE
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_URL = "https://api.openai.com/v1/responses"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

PAYLOAD = {
    "model": "gpt-5.4-mini",
    "instructions": SYSTEM_INSTRUCTIONS,
    "input": query
}

response = requests.post(OPENAI_URL,
    headers=HEADERS,
    data=json.dumps(PAYLOAD)
)

print("AI RESPONSE\n")
RAW_AI_RESPONSE = response.json()
AI_OUTPUT_TEXT = RAW_AI_RESPONSE['output'][0]['content'][0]['text']
print(AI_OUTPUT_TEXT)