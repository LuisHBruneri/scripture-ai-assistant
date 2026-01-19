from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
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
            model=settings.GOOGLE_MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3
        )

        # In-memory history storage
        self.store = {}
        
        # 1. System Prompt for Reformulating Questions (Contextualization)
        self.reformulate_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        self.reformulate_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.reformulate_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        self.reformulate_chain = self.reformulate_prompt | self.llm | StrOutputParser()
        
        # 2. System Prompt for Theological Reasoning (The "Brain" Upgrade)
        self.system_prompt = (
            "You are a sophisticated Theological AI Assistant, designed to reason like a scholar and pastor. "
            "Your goal is not just to retrieve text, but to synthesize it into a coherent, historically grounded, and biblically sound answer.\n\n"
            "Follow this 'Theological Chain of Thought':\n"
            "1. **Analyze Context**: Understand the historical and literary context of the provided scripture/text.\n"
            "2. **Synthesize**: Combine multiple sources to form a complete picture.\n"
            "3. **Compare**: If applicable, mention how this relates to other major doctrines (Analogia Fidei).\n"
            "4. **Apply**: Conclude with a brief practical or pastoral application.\n\n"
            "Tone: Reverent, academic yet accessible, and humble.\n"
            "Constraint: Use ONLY the provided context. If the context is insufficient, state clearly what is missing "
            "but try to answer as much as possible from what is there.\n\n"
            "Context:\n{context}"
        )
        
        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        if session_id not in self.store:
            # In a real app, integrate with Redis or similar here
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    async def get_answer_stream(self, query: str, session_id: str):
        """
        Generates a streaming response with memory and reasoning.
        """
        session_history = self.get_session_history(session_id)
        history_messages = session_history.messages
        
        # Step 1: Reformulate Query (if history exists)
        standalone_query = query
        if history_messages:
            try:
                standalone_query = await self.reformulate_chain.ainvoke({
                    "chat_history": history_messages,
                    "input": query
                })
            except Exception as e:
                print(f"Error formulating query: {e}")
        
        # Step 2: Retrieve Docs (using the polished query)
        docs = await self.retriever.ainvoke(standalone_query)
        context_text = format_docs(docs)
        
        # Step 3: Stream Answer
        # We pass history mostly for context, but the reformulation did the heavy lifting for retrieval.
        # The chain needs 'chat_history' because of MessagesPlaceholder
        chain_with_context = (
            {"context": lambda x: context_text, "chat_history": lambda x: history_messages, "input": RunnablePassthrough()}
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        full_answer = ""
        async for chunk in chain_with_context.astream(query):
            full_answer += chunk
            yield {"type": "content", "data": chunk}
            
        # Step 4: Update History
        session_history.add_user_message(query)
        session_history.add_ai_message(full_answer)
            
        # Yield sources at the end
        unique_sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
        yield {"type": "sources", "data": unique_sources}

    def get_answer(self, query: str, session_id: str = "default"):
        # Synchronous version fallback (updated for consistency, though unused by stream endpoint)
        session_history = self.get_session_history(session_id)
        messages = session_history.messages
        
        docs = self.retriever.invoke(query)
        context_text = format_docs(docs)
        
        chain_with_context = (
            {"context": lambda x: context_text, "chat_history": lambda x: messages, "input": RunnablePassthrough()}
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        answer = chain_with_context.invoke(query)
        session_history.add_user_message(query)
        session_history.add_ai_message(answer)
        
        return {
            "answer": answer,
            "source_documents": [doc.metadata for doc in docs]
        }
