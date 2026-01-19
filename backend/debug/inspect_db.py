import chromadb
from backend.core.config import settings
import sys

def inspect():
    print("🔍 Conectando ao ChromaDB...")
    try:
        client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
        collection = client.get_collection("scripture_corpus")
        
        count = collection.count()
        print(f"📊 Total de Fragmentos (Chunks): {count}")
        
        if count == 0:
            print("⚠️  O banco de dados está vazio.")
            return

        # Fetch metadata to see sources (limit to first 10000 to be safe, though usually fine)
        # We just want unique sources
        print("📂 Analisando fontes...")
        result = collection.get(include=["metadatas"])
        metadatas = result.get("metadatas", [])
        
        sources = set()
        for meta in metadatas:
            if meta and "source" in meta:
                sources.add(meta["source"])
        
        print("\n📚 Arquivos Indexados:")
        if not sources:
            print("   (Nenhuma fonte encontrada nos metadados)")
        else:
            for source in sorted(sources):
                print(f"   - {source}")
                
    except Exception as e:
        print(f"❌ Erro ao inspecionar banco: {e}")

if __name__ == "__main__":
    inspect()
