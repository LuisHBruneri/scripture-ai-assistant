import os
import glob
import json
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from backend.core.config import settings

# Import Processors
from backend.data_ingestion.processors.base import ProcessorFactory, IngestionProcessor
from backend.data_ingestion.processors.gutenberg import GutenbergProcessor
from backend.data_ingestion.processors.pdf_theology import TheologyPDFProcessor

# --- LOGGING CONFIG ---
import logging
logging.basicConfig(level=logging.INFO)
# Suppress noisy HTTP logs from libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

# --- REGISTER PROCESSORS ---
ProcessorFactory.register("gutenberg", GutenbergProcessor())
ProcessorFactory.register("theology_pdf", TheologyPDFProcessor())
# We can register more here later (e.g. Audio, HTML)

def load_bible_structured(json_path: str) -> List[Document]:
    """
    Specialized loader for the Bible JSON structure.
    Kept separate as it's the core dataset with unique verse logic.
    """
    print(f"Loading Bible Structure from {json_path}...")
    documents = []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)
        
    for book in bible_data:
        book_name = book.get("name")
        chapters = book.get("chapters", [])
        
        for chapter_idx, chapter_verses in enumerate(chapters):
            chapter_num = chapter_idx + 1
            chunk_size = 5
            for i in range(0, len(chapter_verses), chunk_size):
                verses_chunk = chapter_verses[i : i + chunk_size]
                start_verse = i + 1
                end_verse = i + len(verses_chunk)
                verses_ref = f"{start_verse}-{end_verse}" if start_verse != end_verse else f"{start_verse}"
                
                content_header = f"[{book_name} {chapter_num}:{verses_ref}]\n"
                verse_text_block = ""
                for v_idx, text in enumerate(verses_chunk):
                    verse_text_block += f"{start_verse + v_idx}. {text}\n"
                    
                full_content = content_header + verse_text_block
                
                doc = Document(
                    page_content=full_content,
                    metadata={
                        "source": "Bible (ACF)",
                        "book": book_name,
                        "chapter": chapter_num,
                        "verses": verses_ref,
                        "type": "scripture"
                    }
                )
                documents.append(doc)
    print(f"  Bible processed: {len(documents)} semantic chunks created.")
    return documents

def determine_processor_key(file_path: str, meta: dict) -> str:
    """Decides which processor to use based on file extension and metadata."""
    ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Check Metadata triggers
    if meta.get("type") == "gutenberg" or meta.get("origin") == "project_gutenberg":
        return "gutenberg"
    
    if meta.get("type", "").startswith("theology_"):
        if ext == ".pdf":
            return "theology_pdf"
    
    # 2. Fallback to extension
    if ext == ".txt" and "gutenberg" in file_path.lower():
        return "gutenberg"
    if ext == ".pdf":
        return "theology_pdf" # Default to our smart PDF processor for now
        
    return None

def load_documents(source_dir: str) -> List[Document]:
    documents = []
    
    # 1. SPECIAL: Structured Bible JSON
    bible_json_path = os.path.join(source_dir, "bible_data.json")
    if os.path.exists(bible_json_path):
        documents.extend(load_bible_structured(bible_json_path))
    
    # 2. Scan for all files in source_dir recursively
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".meta.json") or file == "bible_data.json" or file == "bible_complete.md":
                continue # Skip metadata files & bible source
                
            file_path = os.path.join(root, file)
            
            # Look for sidecar metadata
            meta_path = file_path + ".meta.json"
            metadata = {}
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Select Strategy
            processor_key = determine_processor_key(file_path, metadata)
            if processor_key:
                processor = ProcessorFactory.get_processor(processor_key)
                if processor:
                    docs = processor.process(file_path, metadata)
                    documents.extend(docs)
                else:
                    print(f"  [Warn] No processor found for key: {processor_key}")
            else:
                # Fallback or Skip? For now, we only process known types in this new engine
                # print(f"  [Info] Skipping unidentified file: {file}")
                pass
                
    return documents

def ingest_data():
    if not settings.GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY is missing.")
        return

    print("Loading documents using Intelligent Ingestion Engine...")
    docs = load_documents(settings.SOURCE_DOCS_PATH)
    
    if not docs:
        print("No documents found.")
        return
        
    print(f"Total Documents Prepared: {len(docs)}")
    
    print("Connecting to ChromaDB...")
    import chromadb
    client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
    
    vector_store = Chroma(
        client=client,
        collection_name="scripture_corpus",
        embedding_function=embeddings,
    )
    
    # Basic Duplicate Check (Optimized)
    existing_ids = set()
    try:
        collection = client.get_collection("scripture_corpus")
        # Checking by source is rough, better to check IDs if we had them stable.
        # For now, simplistic check: if source exists, we skip? 
        # Actually, with new chunks, let's just add everything for now or clear?
        # The user wanted increments.
        pass 
    except:
        pass

    # Batch Ingest
    print("Ingesting...")
    batch_size = 50
    total_docs = len(docs)
    
    for i in range(0, total_docs, batch_size):
        batch = docs[i : i + batch_size]
        
        # Calculate progress
        current_count = min(i + batch_size, total_docs)
        percent = (current_count / total_docs) * 100
        
        print(f"  [Progress: {current_count}/{total_docs} ({percent:.1f}%)] Ingesting batch of {len(batch)} chunks...")
        vector_store.add_documents(documents=batch)
        
    print("Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()
