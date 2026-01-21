from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from collections import Counter
from .base import IngestionProcessor

class TheologyPDFProcessor(IngestionProcessor):
    def process(self, file_path: str, metadata: Dict = {}) -> List[Document]:
        print(f"  [TheologyPDFProcessor] Processing {file_path}...")
        try:
            loader = PyPDFLoader(file_path)
            raw_docs = loader.load()
            
            # --- INTELLIGENT CLEANING ---
            # Analyze lines to find repetitive headers/footers
            all_lines = []
            for doc in raw_docs:
                lines = doc.page_content.split('\n')
                # Normalize lines (strip whitespace)
                clean_lines = [l.strip() for l in lines if len(l.strip()) > 5]
                all_lines.extend(clean_lines)
            
            # Find lines that appear on > 30% of pages (likely headers/footers)
            line_counts = Counter(all_lines)
            total_pages = len(raw_docs)
            threshold = total_pages * 0.3 
            
            repetitive_lines = {line for line, count in line_counts.items() if count > threshold}
            
            if repetitive_lines:
                print(f"    Detected {len(repetitive_lines)} repetitive header/footer lines.")

            # Reconstruct content without repetitive lines
            full_text = ""
            for doc in raw_docs:
                lines = doc.page_content.split('\n')
                filtered_lines = [l for l in lines if l.strip() not in repetitive_lines]
                full_text += "\n".join(filtered_lines) + "\n\n"

            # Enhance Metadata
            doc_metadata = metadata.copy()
            doc_metadata["processor"] = "theology_pdf"
            
            # Split Text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=150
            )
            
            texts = text_splitter.split_text(full_text)
            
            docs = []
            for chunk in texts:
                docs.append(Document(page_content=chunk, metadata=doc_metadata))
                
            return docs

        except Exception as e:
            print(f"    Error processing PDF {file_path}: {e}")
            return []
