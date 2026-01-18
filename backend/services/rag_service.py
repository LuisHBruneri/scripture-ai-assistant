from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from backend.core.config import settings
import chromadb

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class RAGService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        # Connect to ChromaDB
        self.chroma_client = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name="scripture_corpus",
            embedding_function=self.embeddings,
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3
        )
        
        self.system_prompt = (
            "You are a wise and knowledgeable theological assistant. "
            "Your purpose is to answer biblical and doctrinal questions with accuracy, "
            "humility, and a pastoral tone. "
            "Use ONLY the following context to answer the user's question. "
            "Do not make up information or use outside knowledge not present in the context. "
            "If the answer is not in the context, say so politely. "
            "Cite biblical references when applicable based on the context provided. "
            "\n\n"
            "Context:\n{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{input}"),
            ]
        )
        
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # Pure LCEL RAG Chain
        self.rag_chain = (
            {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def get_answer(self, query: str):
        # We need to fetch sources manually if we want to return them, 
        # but with simple LCEL, we only get the answer string usually.
        # To get sources, we can retrieve first or use a more complex chain.
        # For MVP, let's retrieve explicitly to return sources, then run generation.
        
        docs = self.retriever.invoke(query)
        context_text = format_docs(docs)
        
        # Invoke chain with pre-fetched context
        chain_with_context = (
            {"context": lambda x: context_text, "input": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain_with_context.invoke(query)
        
        return {
            "answer": answer,
            "source_documents": [doc.metadata for doc in docs]
        }
