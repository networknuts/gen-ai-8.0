import requests 
from dotenv import load_dotenv
import os 

load_dotenv()

weather_api_key = os.getenv("WEATHER_API_KEY")
weather_country_code = input("Enter your country code: ")
weather_zip_code = input("Enter your zip code: ")

weather_url = f"https://api.openweathermap.org/data/2.5/weather?zip={weather_zip_code},{weather_country_code}&appid={weather_api_key}"

response = requests.get(weather_url)

weather_output = response.json()
print(weather_output)