from dotenv import load_dotenv
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END 
from langchain_openai import ChatOpenAI 
from typing import TypedDict, Optional
import json 
from neo4j import GraphDatabase
import os 

# SETUP THE ENVIRONMENT
load_dotenv()
llm = ChatOpenAI(
    model="gpt-5.4-mini"
)

# SETUP NEO4J CONNECTION
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_AUTH = (NEO4J_USER,NEO4J_PASSWORD)

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,auth=NEO4J_AUTH
)

# DEFINE THE STATE

class ChatState(TypedDict):
    user_id: str 
    user_query: str 
    ai_reply: str 
    store_memory: Optional[bool]
    extracted_facts: Optional[list]


# NODE 1: CHAT NODE 
def chat_node(state: ChatState):
    response = llm.invoke(state['user_query'])
    state['ai_reply'] = response.content 
    print(f"AI RESPONSE: \n {state['ai_reply']}")
    return state 

# NODE 2: MEMORY CLASSIFIER NODE
def memory_classifier(state: ChatState):
    prompt = f"""
    You are a user profile memory classifier.
    Determine whether this message contains any 
    long-term personal information about the user.

    Return the output in the following JSON format:
    {{
        "store": true or false,
        "facts": [list of extracted facts containing long term info]
    }}

    User Message:
    {state['user_query']}
    """
    response = llm.invoke(prompt)
    decision = json.loads(response.content) # str to dict
    state['store_memory'] = decision['store']
    state['extracted_facts'] = decision['facts']
    return state 

# NODE 3: SAVE TO NEO4J
def neo4j_save(state: ChatState):
    if not state['extracted_facts']:
        return state 
    else:
        with neo4j_driver.session() as session:
            for fact in state['extracted_facts']:
                session.run(
                    """
                    MERGE (u: User {id: $user_id})
                    MERGE (m: Memory {text: $fact})
                    MERGE (u)-[:HAS_MEMORY]->(m)
                    """,
                    user_id = state['user_id'],
                    fact=fact
                )
        print("Saved Memory")
        return state 

# CONDITIONAL ROUTER
def router(state: ChatState):
    if state['store_memory']:
        return "neo4j_save"
    else:
        return END 

# BUILD THE GRAPH

graph = StateGraph(ChatState)

graph.add_node("chat", chat_node)
graph.add_node("memory_classifier", memory_classifier)
graph.add_node("neo4j_save",neo4j_save)

graph.set_entry_point("chat")
graph.add_edge("chat","memory_classifier")
graph.add_conditional_edges(
    "memory_classifier",
    router,
    {
        "neo4j_save": "neo4j_save",
        END: END 
    }
)
graph.add_edge("neo4j_save",END)

app = graph.compile()

def run_chat():
    user_id = input("Enter your email: ")

    while True:
        user_query = input("Enter Human Query: ")
        if user_query.lower() == "exit":
            break 
        app.invoke({
            "user_id": user_id,
            "user_query": user_query
        })

run_chat()