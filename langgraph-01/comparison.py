from dotenv import load_dotenv
from openai import OpenAI 
from langchain_openai import ChatOpenAI

load_dotenv()

client = OpenAI()
response = client.responses.create(
    model="gpt-5.4-mini",
    input="what is the best coffee in the world?"
)
print(response.output_text)

llm = ChatOpenAI(model="gpt-5.4-mini")
response = llm.invoke("what is the best coffee in the world?")
print(response.content)