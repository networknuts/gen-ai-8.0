from openai import OpenAI
from dotenv import load_dotenv

# LOAD YOUR .ENV FILE
load_dotenv()

# INITIALIZE THE SYSTEM PROMPT
f = open("chain_of_thought.txt","r")
system_prompt = f.read()
f.close()

# INITIALIZE OPENAI
client = OpenAI()

# ASK FOR USER QUERY
user_query = input("> ")

# CONNECT TO AI ENDPOINT
response = client.responses.create(
    model="gpt-5.5",
    reasoning={"effort": "medium"},
    instructions=system_prompt,
    input=user_query
)

print(response.output_text)
print("="*40)
print(response)