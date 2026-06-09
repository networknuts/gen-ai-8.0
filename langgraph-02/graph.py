from dotenv import load_dotenv
from langgraph.graph import StateGraph, END 
from langchain_openai import ChatOpenAI 
from typing import TypedDict 

# SETUP THE ENVIRONMENT
load_dotenv()
llm_developer = ChatOpenAI(model="gpt-5.4")
llm_qa = ChatOpenAI(model="gpt-5.5")

MAX_RETRIES = 3

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
You are a NodeJS developer. Write code for the given user request.
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

Return the output in the following format:
{{
    "rating": integer value between 1-10,
    "feedback": "clear improvements to make to the code"
}}

Code: 
{state['code']}
    """
    result = llm_qa.invoke(prompt).content
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