from dotenv import load_dotenv
from openai import OpenAI
import requests
import os 
import json 

# SETUP THE ENVIRONMENT
load_dotenv()
client = OpenAI()

f = open("weather_description.txt","r")
weather_function_description = f.read()
f.close()

f = open("orderdata_description.txt","r")
orderdata_function_description = f.read()
f.close()

# TOOL 1: GET WEATHER DATA
def get_weather(zipcode):
    weather_api_key = os.getenv("WEATHER_API_KEY")
    weather_country_code = "in"
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?zip={zipcode},{weather_country_code}&appid={weather_api_key}"
    response = requests.get(weather_url)
    result = response.json()
    return result 

# TOOL 2: GET ORDER STATUS
def get_order_data(user_id):
    url = f"http://localhost:8000/delivery/{user_id}"
    result = requests.get(url)
    if result.status_code != 200:
        return {"error": "user not found"}
    else:
        return result.json()
    
# TOOL SCHEMA

openai_tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": weather_function_description,
        "parameters": {
            "type": "object",
            "properties": {
                "zipcode": {
                    "type": "string",
                    "description": "the zipcode of the location you want to get the weather data of."
                },
            },
            "required": ["zipcode"],
        }
    },
    {
        "type": "function",
        "name": "get_order_data",
        "description": orderdata_function_description,
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "The ID of the user"
                }
            },
            "required": ["user_id"],
        }
    }
]

# ASK FOR USER QUERY
user_query = input("Human Query: ")


# RUN THE LLM CALL
response = client.responses.create(
    model="gpt-5.4-mini",
    input=user_query,
    tools=openai_tools
)

tool_output = []

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        if item.name == "get_weather":
            result = get_weather(args['zipcode'])
        elif item.name == "get_order_data":
            result = get_order_data(args['user_id'])
        else:
            result = "unknown tool called"

        tool_output.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({"result": result})
        })

# SECOND LLM CALL TO CONVERT RAW TOOL OUTPUT TO POLISHED OUTPUT

final_response = client.responses.create(
    model="gpt-5.4-mini",
    input=tool_output,
    previous_response_id=response.id
)

print(final_response.output_text)