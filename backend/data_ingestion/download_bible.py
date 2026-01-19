import urllib.request
import json
import os

# Source: Thiago Bodruk's Bible Repo (Open Source JSONs)
# Using Almeida Corrigida Fiel (pt_acf)
URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_acf.json"
OUTPUT_FILE = "source_docs/bible_complete.md"

def download_and_convert():
    print(f"📥 Baixando Bíblia de {URL}...")
    try:
        with urllib.request.urlopen(URL) as response:
            data = response.read().decode("utf-8-sig")
            bible_data = json.loads(data)
            
        # Save JSON for structured ingestion
        with open("source_docs/bible_data.json", "w", encoding="utf-8") as f:
            json.dump(bible_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"❌ Erro ao baixar: {e}")
        return

    print("📖 Convertendo para Markdown...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Loop through books
        for book in bible_data:
            book_name = book.get("name")
            print(f"   Processando {book_name}...")
            
            # Write Book Header
            # f.write(f"# {book_name}\n\n") 
            # Note: Depending on chunking, maybe just Chapter headers are better to keep context tight.
            # Let's use H1 for Book, H2 for Chapter.
            
            chapters = book.get("chapters", [])
            for chapter_idx, chapter in enumerate(chapters):
                params = {
                    "book": book_name,
                    "chapter": chapter_idx + 1
                }
                
                # Header: Gênesis 1
                f.write(f"# {book_name} {chapter_idx + 1}\n\n")
                
                # Verses
                for verse_idx, verse_text in enumerate(chapter):
                    # Format: 1. No princípio...
                    f.write(f"{verse_idx + 1}. {verse_text}\n")
                
                f.write("\n---\n\n") # Separator between chapters
    
    print(f"✅ Bíblia salva em '{OUTPUT_FILE}'!")
    print("🚀 Agora execute './refresh_knowledge.sh' para ingerir os dados.")

if __name__ == "__main__":
    download_and_convert()
