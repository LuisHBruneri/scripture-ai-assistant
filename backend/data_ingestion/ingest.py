import os
import glob
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from backend.core.config import settings

import json
from langchain_core.documents import Document

def load_bible_structured(json_path: str) -> List[Document]:
    print(f"Loading Bible Structure from {json_path}...")
    documents = []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)
        
    for book in bible_data:
        book_name = book.get("name")
        chapters = book.get("chapters", [])
        
        for chapter_idx, chapter_verses in enumerate(chapters):
            chapter_num = chapter_idx + 1
            
            # Semantic Chunking: Group verses (e.g., 5 verses per chunk)
            chunk_size = 5
            for i in range(0, len(chapter_verses), chunk_size):
                verses_chunk = chapter_verses[i : i + chunk_size]
                start_verse = i + 1
                end_verse = i + len(verses_chunk)
                verses_ref = f"{start_verse}-{end_verse}" if start_verse != end_verse else f"{start_verse}"
                
                # Create Content with explicit context header
                content_header = f"[{book_name} {chapter_num}:{verses_ref}]\n"
                
                verse_text_block = ""
                for v_idx, text in enumerate(verses_chunk):
                    verse_num = start_verse + v_idx
                    verse_text_block += f"{verse_num}. {text}\n"
                    
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

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

class CustomEpubLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Document]:
        try:
            book = epub.read_epub(self.file_path)
            documents = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Ignore navigation files if possible, but simplest is just check text content
                    try:
                        content = item.get_content().decode('utf-8')
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text()
                        if len(text.strip()) > 50: # Filter empty/tiny chapters
                             documents.append(Document(
                                 page_content=text,
                                 metadata={"source": os.path.basename(self.file_path)}
                             ))
                    except:
                        continue 
            return documents
        except Exception as e:
            print(f"Error loading EPUB {self.file_path}: {e}")
            return []

def load_documents(source_dir: str) -> List[Document]:
    documents = []
    
    # 1. SPECIAL: Structured Bible JSON
    bible_json_path = os.path.join(source_dir, "bible_data.json")
    if os.path.exists(bible_json_path):
        documents.extend(load_bible_structured(bible_json_path))
    
    # 2. Load PDFs
    for file_path in glob.glob(os.path.join(source_dir, "**/*.pdf"), recursive=True):
        print(f"Loading {file_path}...")
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    
    # 3. Load EPUBs
    for file_path in glob.glob(os.path.join(source_dir, "**/*.epub"), recursive=True):
        print(f"Loading {file_path}...")
        loader = CustomEpubLoader(file_path)
        documents.extend(loader.load())

    # 4. Load Markdown files (Skip bible_complete.md to avoid double ingestion)
    for file_path in glob.glob(os.path.join(source_dir, "**/*.md"), recursive=True):
         if "bible_complete.md" in file_path and os.path.exists(bible_json_path):
             print(f"Skipping {file_path} (Using structured JSON instead)")
             continue
             
         print(f"Loading {file_path}...")
         loader = TextLoader(file_path)
         documents.extend(loader.load())
    
    return documents

def split_documents(documents: List[Document]):
    # Separate pre-chunked (Bible) from raw docs
    pre_chunked = [doc for doc in documents if doc.metadata.get("type") == "scripture"]
    raw_docs = [doc for doc in documents if doc.metadata.get("type") != "scripture"]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    split_raw = text_splitter.split_documents(raw_docs)
    
    # Combine both
    return pre_chunked + split_raw

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
    
    print("Initializing Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=settings.GOOGLE_API_KEY)
    
    print("Connecting to ChromaDB...")
    import chromadb
    client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
    
    vector_store = Chroma(
        client=client,
        collection_name="scripture_corpus",
        embedding_function=embeddings,
    )
    
    # --- DUPLICATE PROTECTION ---
    print("Checking for existing documents...")
    try:
        # Get all metadatas to find unique sources
        collection = client.get_collection("scripture_corpus")
        # We need to fetch metadata to check for existing books
        existing_data = collection.get(include=["metadatas"])
        
        existing_keys = set()
        for meta in existing_data.get("metadatas", []):
            if meta:
                source = meta.get("source", "unknown")
                book = meta.get("book", None) # Bible chunks have 'book'
                existing_keys.add((source, book))
        
        print(f"Found {len(existing_keys)} existing unique (source, book) entries in database.")
    except Exception as e:
        print(f"Warning: Could not check duplicates ({e}). Assuming empty DB.")
        existing_keys = set()

    # Filter docs
    new_docs = []
    skipped_count = 0
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        book = doc.metadata.get("book", None)
        
        if (source, book) in existing_keys:
            skipped_count += 1
        else:
            new_docs.append(doc)
            
    if skipped_count > 0:
        print(f"⚠️  Skipping {skipped_count} chunks (already ingested).")
    
    if not new_docs:
        print("✅ No new documents to ingest. Everything is up to date!")
        return

    print(f"Preparing to ingest {len(new_docs)} new chunks...")
    chunks = split_documents(new_docs) 
    print(f"Split into {len(chunks)} chunks.")
    
    print("Ingesting into ChromaDB...")
    
    # Process in smaller batches to avoid timeouts
    batch_size = 50 
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        print(f"Ingesting batch {i // batch_size + 1}/{len(chunks) // batch_size + 1} ({len(batch)} chunks)...")
        # Retry logic is handled by langchain/tenacity mostly, but smaller batch helps
        vector_store.add_documents(documents=batch)
        
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
