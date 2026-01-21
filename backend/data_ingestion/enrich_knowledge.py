import os
import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from urllib.parse import urlparse

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
SOURCE_DOCS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../source_docs"))
os.makedirs(SOURCE_DOCS_PATH, exist_ok=True)

# --- ARCHITECTURE: SOURCE STRATEGY PATTERN ---

class ContentSource(ABC):
    """Abstract Base Class for different content sources (URL, API, Scraper)."""
    
    @abstractmethod
    def fetch_resources(self) -> List[Dict]:
        """Returns a list of resource dicts: {title, author, url, type, etc.}"""
        pass

    def download_file(self, url: str, filename: str) -> Optional[str]:
        """Helper to download a file safely."""
        try:
            target_path = os.path.join(SOURCE_DOCS_PATH, filename)
            if os.path.exists(target_path):
                logger.info(f"Skipping {filename} (already exists).")
                return target_path

            logger.info(f"Downloading {filename} from {url}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded {filename}.")
            return target_path
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

    def save_metadata(self, file_path: str, metadata: Dict):
        """Saves a sidecar .meta.json file for the ingestion engine."""
        if not file_path: return
        
        meta_path = file_path + ".meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

# --- IMPLEMENTATION 1: DIRECT CURATED LIST ---

class DirectURLSource(ContentSource):
    def fetch_resources(self) -> List[Dict]:
        return [
            {
                "title": "Confissões",
                "author": "Santo Agostinho",
                "year": 400,
                "url": "https://img.cancaonova.com/noticias/pdf/277537_SantoAgostinho-Confissoes.pdf",
                "filename": "Santo_Agostinho_Confissoes.pdf",
                "type": "theology_patristic"
            },
            {
                "title": "Institutas da Religião Cristã (Tomo I)",
                "author": "João Calvino",
                "year": 1536,
                "url": "https://ecasolli.files.wordpress.com/2017/08/joao-calvino-a-instituicao-da-religiao-crista-tomo-i-unesp.pdf",
                "filename": "Joao_Calvino_Institutas_Tomo_I.pdf",
                "type": "theology_reformed"
            },
            {
                "title": "Confissão de Fé de Westminster",
                "author": "Assembleia de Westminster",
                "year": 1646,
                "url": "https://www.executivaipb.com.br/arquivos/confissao_de_westminster.pdf",
                "filename": "Confissao_Westminster.pdf",
                "type": "confessional"
            },
             {
                "title": "O Peregrino",
                "author": "John Bunyan",
                "year": 1678,
                "url": "https://cavcomunidade.files.wordpress.com/2017/10/o-peregrino-john-bunyan.pdf",
                "filename": "John_Bunyan_O_Peregrino.pdf",
                "type": "christian_literature"
            }
        ]

    def run(self):
        resources = self.fetch_resources()
        for res in resources:
            file_path = self.download_file(res['url'], res['filename'])
            if file_path:
                # Prepare metadata for sidecar
                meta = {
                    "source": res['filename'],
                    "title": res['title'],
                    "author": res['author'],
                    "year": res['year'],
                    "type": res['type'],
                    "origin": "curated_url"
                }
                self.save_metadata(file_path, meta)

# --- IMPLEMENTATION 2: PROJECT GUTENBERG (Gutendex API) ---

class GutenbergSource(ContentSource):
    BASE_URL = "https://gutendex.com/books"

    def __init__(self, topic="Christianity", lang="pt"):
        self.topic = topic
        self.lang = lang

    def fetch_resources(self) -> List[Dict]:
        logger.info(f"Searching Gutenberg for topic '{self.topic}' in '{self.lang}'...")
        try:
            params = {
                "topic": self.topic,
                "languages": self.lang,
                "sort": "popular" 
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            data = response.json()
            
            results = []
            for book in data.get('results', []):
                # Find text/plain format
                txt_url = book['formats'].get('text/plain; charset=utf-8')
                if not txt_url:
                    continue # Skip if no clean text available
                
                authors = [a['name'] for a in book.get('authors', [])]
                author_name = authors[0] if authors else "Unknown"
                
                results.append({
                    "title": book['title'],
                    "author": author_name,
                    "url": txt_url,
                    "id": book['id'],
                    "type": "gutenberg_book"
                })
            
            logger.info(f"Found {len(results)} books on Gutenberg.")
            return results

        except Exception as e:
            logger.error(f"Gutenberg API failed: {e}")
            return []

    def run(self):
        books = self.fetch_resources()
        for book in books:
            # Create safe filename
            safe_title = "".join([c if c.isalnum() else "_" for c in book['title']])[:50]
            filename = f"Gutenberg_{book['id']}_{safe_title}.txt"
            
            file_path = self.download_file(book['url'], filename)
            if file_path:
                meta = {
                    "source": filename,
                    "title": book['title'],
                    "author": book['author'],
                    "type": "gutenberg",
                    "gutenberg_id": book['id'],
                    "origin": "project_gutenberg"
                }
                self.save_metadata(file_path, meta)

# --- MAIN CONTROLLER ---

def main():
    print("=== Starting Intelligent Knowledge Enrichment ===")
    
    # 1. Direct Sources
    print("\n--- Processing Curated Resources ---")
    direct = DirectURLSource()
    direct.run()
    
    # 2. Gutenberg Sources (Theology/Religion)
    print("\n--- Processing Project Gutenberg ---")
    # Search for 'Christianity', 'Religion', 'Theology'
    topics = ["Christianity", "Religion", "Theology", "Bible"]
    for topic in topics:
        gutenberg = GutenbergSource(topic=topic, lang="pt")
        gutenberg.run()

    print("\n=== Enrichment Complete. Checks 'source_docs' ===")

if __name__ == "__main__":
    main()
