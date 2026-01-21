from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base import IngestionProcessor

class GutenbergProcessor(IngestionProcessor):
    def process(self, file_path: str, metadata: Dict = {}) -> List[Document]:
        print(f"  [GutenbergProcessor] Processing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        # Clean Gutenberg Headers/Footers
        # They usually have "*** START OF THE PROJECT GUTENBERG EBOOK"
        start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
        end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
        
        start_idx = text.find(start_marker)
        if start_idx != -1:
            # Move past the marker line
            text = text[start_idx:]
            # Find next newline to skip the marker line itself
            newline_idx = text.find('\n')
            if newline_idx != -1:
                text = text[newline_idx+1:]
        
        end_idx = text.find(end_marker)
        if end_idx != -1:
            text = text[:end_idx]

        # Enhance Metadata
        doc_metadata = metadata.copy()
        doc_metadata["processor"] = "gutenberg"
        
        # Split Text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, # Slightly larger for narratives
            chunk_overlap=200,
            separators=["\n\n", ". ", " ", ""]
        )
        
        texts = text_splitter.split_text(text)
        
        docs = []
        for chunk in texts:
            docs.append(Document(page_content=chunk, metadata=doc_metadata))
            
        return docs
