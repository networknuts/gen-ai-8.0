from dotenv import load_dotenv
from langgraph.graph import StateGraph, END 
from langchain_openai import ChatOpenAI 
from typing import TypedDict
import json 
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

# SETUP THE ENVIRONMENT
load_dotenv()
llm_developer = ChatOpenAI(model="gpt-5.4-mini")
llm_qa = ChatOpenAI(model="gpt-5.5")

MAX_RETRIES = 3

client = MongoClient("mongodb://localhost:27017")
memory = MongoDBSaver(client)

# DEFINE YOUR STATE

class CodeState(TypedDict):
    user_request: str 
    code: str 
    rating: int 
    feedback: str 
    retries: int 
    status: str #running / approved / failed


# AGENT 1: DEVELOPER AGENT
def developer_agent(state: CodeState):
    prompt = f"""
You are a NodeJS developer. Write intentionally poor code for the given user request.
User Request: {state['user_request']}

If feedback is provided, improve the previous version of the code.
Previous Code:
{state['code']}

Feedback:
{state['feedback']}
    """
    result = llm_developer.invoke(prompt).content
    return {
        "code": result,
        "feedback": ""
    }

# AGENT 2: QA AGENT
def qa_agent(state: CodeState):
    prompt = f"""
You are a senior NodeJS QA Engineer.
Evaluate the following NodeJS code for the given requirements:
- Correctness of the code
- Structure of the code
- Readability of the code
- Whether best production practices are being followed
- Error handling capability of the code
- Scalability factor in the code

Return the output in the following JSON format:
{{
    "rating": integer value between 1-10,
    "feedback": "clear improvements to make to the code"
}}

Code: 
{state['code']}
    """
    llm_output = llm_qa.invoke(prompt).content.strip()
    result = json.loads(llm_output)
    return {
        "rating": int(result['rating']),
        "feedback": result['feedback']
    }

# NODE: APPROVED STATUS
def set_approved(state: CodeState):
    return {
        "status": "approved"
    }

# NODE: FAILED STATUS
def set_failed(state: CodeState):
    return {
        "status": "failed"
    }

# NODE: INCREMENTAL RETRY LOGIC
def increment_retry(state: CodeState):
    return {
        "retries": state['retries']+1
    }

# CONDITIONAL ROUTER
def check_rating(state: CodeState):
    if state['rating'] >= 7:
        return "approved"
    if state['retries'] >= MAX_RETRIES:
        return "failed"
    return "retry"

# GRAPH BUILDING
graph = StateGraph(CodeState)

graph.add_node("developer",developer_agent)
graph.add_node("qa",qa_agent)
graph.add_node("approved_node",set_approved)
graph.add_node("failed_node",set_failed)
graph.add_node("retry",increment_retry)

graph.set_entry_point("developer")
graph.add_edge("developer","qa")
graph.add_conditional_edges(
    "qa",
    check_rating,
    {
        "approved": "approved_node",
        "failed": "failed_node",
        "retry": "retry"
    }
)
graph.add_edge("approved_node",END)
graph.add_edge("failed_node",END)
graph.add_edge("retry","developer")

app = graph.compile(checkpointer=memory)

# UNIQUE IDENTIFIERS

user_id = "2"
session_id = "1"

thread_id = f"{user_id}:{session_id}"
# CHECK FOR EXISTING EXECUTION

existing = memory.get({"configurable": {"thread_id":thread_id }})

try:
    if existing:
        print("RESUMING FROM CHECKPOINT")
        result = app.invoke({},config={"configurable": {"thread_id":thread_id }})
    else:
        # ASK FOR USER INPUT
        user_input = input("Enter NodeJS App Description:\n")
        result = app.invoke({
            "user_request": user_input, 
            "code": "",
            "rating": 0,
            "feedback": "",
            "retries": 0,
            "status": "running"
        },config={"configurable": {"thread_id":thread_id }})

    print("\nFINAL OUTPUT\n")
    print(f"Code: {result['code']}")
    print(f"Feedback: {result['feedback']}")
    print(f"Rating: {result['rating']}")
    print(f"Retries: {result['retries']}")
    print(f"Status: {result['status']}")
except Exception as e:
    print(f"Error: {e}")