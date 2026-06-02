from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# ENVIRONMENT SETUP
load_dotenv()

# CONFIGURATION
PDF_FILE = "data.pdf"
EMBEDDING_MODEL = "text-embedding-3-large"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "customer_support_knowledge"

# STEP 1: LOAD THE PDF DOCUMENT
loader = PyPDFLoader(PDF_FILE)

pdf_text = loader.load()

# STEP 2: SPLIT THE TEXT INTO CHUNKS
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunked_text = text_splitter.split_documents(pdf_text)

# STEP 3: CHOOSE EMBEDDING STRATEGY
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# STEP 4: STORE THE CHUNKS IN THE VECTOR DATABASE
qdrant = QdrantVectorStore.from_documents(
    documents=chunked_text,
    embedding=embeddings,
    url=QDRANT_URL,
    prefer_grpc=False,
    collection_name=COLLECTION_NAME
)

print("INGESTION COMPLETED")