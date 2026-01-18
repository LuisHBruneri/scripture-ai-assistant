import sys
import os
import chromadb
from chromadb.config import Settings

# Add backend directory to path to import settings if needed, 
# but for this script we can just read env vars or hardcode for debugging.
# Better to rely on the environment variables passed by docker-compose.

HOST = os.getenv("CHROMADB_HOST", "chromadb")
PORT = os.getenv("CHROMADB_PORT", "8000")

def inspect_chroma():
    print(f"Connecting to ChromaDB at {HOST}:{PORT}...")
    try:
        client = chromadb.HttpClient(host=HOST, port=int(PORT))
        print("✅ Connected successfully.")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    collections = client.list_collections()
    print(f"\nFound {len(collections)} collections:")
    
    for col in collections:
        print(f" - Collection Name: {col.name}")
        # Build collection object to query it
        collection = client.get_collection(name=col.name)
        count = collection.count()
        print(f"   - Document Count: {count}")
        
        if count > 0:
            print("   - Sample Data (first 2 items):")
            # peek returns a dict
            data = collection.peek(limit=2)
            ids = data.get('ids', [])
            metadatas = data.get('metadatas', [])
            documents = data.get('documents', [])
            
            for i, doc_id in enumerate(ids):
                print(f"     [{i+1}] ID: {doc_id}")
                print(f"         Metadata: {metadatas[i]}")
                # Truncate content for display
                content = documents[i][:100].replace('\n', ' ') + "..." if documents[i] else "No content"
                print(f"         Content: {content}")
        print("-" * 30)

if __name__ == "__main__":
    inspect_chroma()
