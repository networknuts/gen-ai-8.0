import redis
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI 
import ast 

# SETUP THE AI  ENVIRONMENT
load_dotenv()
client = OpenAI()
COLLECTION_NAME = "customer_support_knowledge"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "text-embedding-3-large"

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    url=QDRANT_URL,
)

# SETUP THE REDIS ENVIRONMENT
queue_name = "rag:requests"
redis_client = redis.Redis(host='localhost', 
    port=6379, 
    decode_responses=True)

# PULL DATA OUT OF REDIS QUEUE
print("Worker Ready, Waiting for Payload\n")
while True:
    queue_name, raw_payload = redis_client.blpop(queue_name)
    payload = ast.literal_eval(raw_payload)
    job_id = payload['job_id']
    query = payload['query']
    print(f"Processing Job: {job_id}")

    # AI RAG CODE
    search_results = qdrant.similarity_search(query)
    context_list = []
    for result in search_results:
        block = f"""
        Page Content: 
        {result.page_content}
        Page Number:
        {result.metadata.get('page_label','N/A')}
        """
        context_list.append(block)
    SYSTEM_PROMPT = f"""
You are a RAG AI Assistant.
You have been given context extracted from a PDF document.
Each section contains:
- The text content
- The page number

Answer the user's query using only this provided information.
If the answer is available:
- Respond in a clear manner summarizing the data from the PDF context
- Mention the relevant page numbers from where the data was extracted

If the answer is not available:
- State to the user that the required information is not in your knowledge base.

In any circumstances, do not add outside information.

Context:
{context_list}
"""
    response = client.responses.create(
    model="gpt-5.4-mini",
    input=query,
    instructions=SYSTEM_PROMPT
    )
    print(response.output_text)