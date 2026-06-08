from dotenv import load_dotenv
from langgraph.graph import StateGraph, END 
from langchain_openai import ChatOpenAI 
from typing import TypedDict 

# SETUP THE ENVIRONMENT
load_dotenv()
llm = ChatOpenAI(model="gpt-5.4-mini")

# DEFINE THE STATE
class SupportState(TypedDict):
    user_query: str 
    intent: str 
    response: str 

# AGENT 1: INTENT CLASSIFICATION AGENT
def classify_intent(state: SupportState):
    prompt = f"""
    Classify the user query into one of these 3 categories:
    - account_related
    - order_related
    - refund_related

    Only return the category name.

    User Query: {state['user_query']}
    """
    result = llm.invoke(prompt)
    return {
        "intent": result.content.strip().lower()
    }

# AGENT 2: ACCOUNT RELATED AGENT
def handle_account(state: SupportState):
    return {
        "response": "Please click on forget password at the bottom of the page to reset your password."
    }

# AGENT 3: ORDER RELATED AGENT
def handle_order(state: SupportState):
    return {
        "response": "Please click on my orders under your profile to track your order."
    }

# AGENT 4: REFUND RELATED AGENT
def handle_refund(state: SupportState):
    return {
        "response": "We have initiated your refund request."
    }

# ROUTER AGENT / ROUTER NODE
def route_intent(state: SupportState):
    if state["intent"] == "account_related":
        return "handle_account"
    elif state["intent"] == "order_related":
        return "handle_order"
    elif state["intent"] == "refund_related":
        return "handle_refund"
    else:
        return END

# BUILDING THE GRAPH

graph = StateGraph(SupportState)

# PROVIDE GRAPH WITH YOUR NODES INFORMATION
graph.add_node("classifier",classify_intent) #ALIAS OR A NICK NAME
graph.add_node("handle_account",handle_account)
graph.add_node("handle_order",handle_order)
graph.add_node("handle_refund",handle_refund)

graph.set_entry_point("classifier")
graph.add_conditional_edges("classifier",route_intent)
graph.add_edge("handle_order",END)
graph.add_edge("handle_refund",END)
graph.add_edge("handle_account",END)

app = graph.compile()

# EXECUTE THE WORKFLOW
user_input = input("Enter Query: ")

result = app.invoke({
    "user_query": user_input,
    "intent": "",
    "response": ""
})

print(result["intent"])
print(result["response"])