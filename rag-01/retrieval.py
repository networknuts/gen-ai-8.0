from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI 

# ENVIRONMENT SETUP
load_dotenv()
client = OpenAI()

COLLECTION_NAME = "customer_support_knowledge"
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "text-embedding-3-large"

# STEP 1: INITIALIZE THE EMBEDDING MODEL - SAME AS INGESTION
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# STEP 2: CONNECT TO THE VECTOR DATABASE WITH RELEVANT COLLECTION
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    url=QDRANT_URL,
)

# STEP 3: ASK FOR USER QUERY
query = input("Human Query: ")

# STEP 4: PERFORM SIMILARITY SEARCH
search_results = qdrant.similarity_search(query) # k=4, which means top 4 chunks only

# STEP 5: BUILD CONTEXT OF OUT THE CHUNKS
context_list = []

for result in search_results:
    block = f"""
    Page Content: 
    {result.page_content}
    Page Number:
    {result.metadata.get('page_label','N/A')}
    """
    context_list.append(block)

# STEP 6: CREATE A RAG SYSTEM PROMPT
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

# STEP 7: GENERATE LLM RESPONSE
response = client.responses.create(
    model="gpt-5.4-mini",
    input=query,
    instructions=SYSTEM_PROMPT
)

print(response.output_text)