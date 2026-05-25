from openai import OpenAI
from dotenv import load_dotenv

# LOAD YOUR .ENV FILE
load_dotenv()

# INITIALIZE OPENAI
client = OpenAI()

# ASK FOR USER QUERY
user_query = input("> ")

# CONNECT TO AI ENDPOINT
response = client.responses.create(
    model="gpt-5.4-mini",
    input=[
        {
            "role": "user",
            "content": "hi my name is anil."
        },
        {
            "role": "assistant",
            "content": "Hi Anil — nice to meet you! How can I help today?"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
)

print(response.output_text)