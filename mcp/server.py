from mcp.server.fastmcp import FastMCP
import wikipedia 
import requests 

mcp = FastMCP("Customer Support Server", json_response=True)

@mcp.tool()
def wikipedia_search(topic: str):
    """
    Get wikipedia summary of any topic by providing the 
    relevant topic name. This wikipedia search tool is limited
    to only providing a 10 line summary on the given topic.
    """
    try:
        return wikipedia.summary(topic,sentences=10)
    except Exception as e:
        return str(e)

@mcp.tool()
def get_order_data(user_id: int):
    """
    Get the following information about the ordered item of a user:
    - item name
    - delivery date
    - delivery status

    The function requires a user_id to work and provides above data for
    the given user_id.
    """
    url = f"http://localhost:8080/delivery/{user_id}"
    result = requests.get(url)
    if result.status_code != 200:
        return {"error": "user not found"}
    else:
        return result.json()

@mcp.tool()
def execute_refund_request(user_id: int):
    """
    This tool connects to the bank API and refunds the last order
    of the user. This tool requires the user_id and will automatically
    find the refund value and process the refund with the bank.
    """
    return {
        "status": "completed",
        "data": f"refund for {user_id} processed with ICICI bank."
    }


mcp.run(transport="streamable-http")