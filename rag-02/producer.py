import redis
import uuid 

# SETUP THE REDIS CONNECTION
redis_client = redis.Redis(host='localhost', 
    port=6379, 
    decode_responses=True)

# GENERATE PAYLOAD AND SEND PAYLOAD TO REDIS

def send_payload(query):
    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "query": query
    }
    queue_name = "rag:requests" #rag:requests | rag:responses
    redis_client.rpush(queue_name,str(payload))
    return job_id

# ASK FOR USER INPUT
query = input("Human Query: ")

# SEND QUERY TO SEND_PAYLOAD FUNCTION
job = send_payload(query)
print("Query sent to Redis successfully!")
print(job)