from abc import ABC, abstractmethod
from typing import List, Dict
from langchain_core.documents import Document

class IngestionProcessor(ABC):
    """Base strategy interface for ingesting different content types."""
    
    @abstractmethod
    def process(self, file_path: str, metadata: Dict = {}) -> List[Document]:
        """
        Process a file and return a list of Documents.
        Args:
            file_path: Absolute path to the file.
            metadata: Optional sidecar metadata (author, title, etc).
        """
        pass

class ProcessorFactory:
    """Registry for ingestion processors."""
    _processors = {}

    @classmethod
    def register(cls, key: str, processor: IngestionProcessor):
        cls._processors[key] = processor

    @classmethod
    def get_processor(cls, key: str) -> IngestionProcessor:
        return cls._processors.get(key)
