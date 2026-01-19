import os
import glob
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from backend.core.config import settings

def load_documents(source_dir: str) -> List:
    documents = []
    # Load PDFs
    for file_path in glob.glob(os.path.join(source_dir, "**/*.pdf"), recursive=True):
        print(f"Loading {file_path}...")
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    
    # Load Markdown files
    for file_path in glob.glob(os.path.join(source_dir, "**/*.md"), recursive=True):
         print(f"Loading {file_path}...")
         loader = TextLoader(file_path)
         documents.extend(loader.load())
    
    return documents

def split_documents(documents: List):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def ingest_data():
    if not settings.GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY is missing.")
        return

    print("Loading documents...")
    docs = load_documents(settings.SOURCE_DOCS_PATH)
    if not docs:
        print("No documents found in source_docs/")
        return
        
    print(f"Loaded {len(docs)} documents.")
    
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")
    
    print("Initializing Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
    
    print("Ingesting into ChromaDB...")
    # Connect to ChromaDB running in Docker
    import chromadb
    client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
    
    # Using LangChain wrapper which automatically handles embedding generation
    vector_store = Chroma(
        client=client,
        collection_name="scripture_corpus",
        embedding_function=embeddings,
    )
    
    # Process in batches to avoid hitting ChromaDB limits (max 5461)
    batch_size = 200
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Ingesting batch {i // batch_size + 1}/{len(chunks) // batch_size + 1} ({len(batch)} chunks)...")
        vector_store.add_documents(documents=batch)
        
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
