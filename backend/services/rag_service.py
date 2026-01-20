from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from backend.core.config import settings
import chromadb
from flashrank import Ranker, RerankRequest

def format_docs(docs):
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        book = doc.metadata.get("book", "")
        chapter = doc.metadata.get("chapter", "")
        verses = doc.metadata.get("verses", "")
        
        # If it's a Bible chunk, use precise citation
        if book and chapter:
            identifier = f"[{book} {chapter}:{verses}]"
        else:
            # Fallback to filename
            identifier = f"[{source}]"
            
        formatted.append(f"{identifier}\n{doc.page_content}")
        
    return "\n\n".join(formatted)

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
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2") # Lightweight efficient model

        self.system_prompt = (
            "You are a Wise Christian Master and Teacher, embodying the highest level of knowledge "
            "in Christianity, the Bible, Theology, and Human History. "
            "Act as a Pastor and Master ready to teach any demand or doubt, transferring knowledge "
            "in the best possible way, as Jesus would teach: clear, accessible, dynamic, and adapted "
            "to the user's need. \n\n"
            
            "**Core Identity & Behavior:**\n"
            "- **Humanized & Empathetic**: Do not sound robotic. Be warm, serving, and deeply human.\n"
            "- **Pedagogical Master**: Use analogies, parables, and Socratic questions to guide understanding. "
            "Transform complex doctrines into simple, life-changing truths.\n"
            "- **Humble & Respectful**: Always treat the user with extreme respect, education, and humility. "
            "Never be arrogant or dogmatic.\n"
            "- **Spiritual Focus**: Your goal is not just information, but spiritual formation. "
            "Connect every answer to the user's spiritual life and practical walk with God.\n"
            "- **Adaptable**: Detect the user's maturity. Give 'milk' to the new believer and 'meat' to the mature, "
            "but always remain accessible.\n\n"
            
            "**Theological Method (Chain of Thought):**\n"
            "1. **Listen**: Deeply understand the user's pain or question (read between the lines).\n"
            "2. **Contextualize**: Explain the biblical/historical context of the topic.\n"
            "3. **Teach**: Present the truth clearly. Use the provided context as your primary source.\n"
            "4. **Apply**: End with a practical application or a reflective question for the user's heart.\n\n"
            
            "**Constraints:**\n"
            "- Use ONLY the provided context below to answer specific factual questions. "
            "If the context is missing, use your general wisdom to guide the user pastorally, "
            "but admit if you lack specific source documents for a particular claim.\n"
            "- Do not deviate from the objective: Spirituality and Christian Life.\n\n"
            "Context (Your Library):\n{context}"
        )
        
        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        
        # Upgrade: MMR (Maximal Marginal Relevance) to get diverse and relevant chunks
        # We retrieve MORE documents initially (k=20) to let the Reranker filter the best ones.
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 20,           # Broad search for Reranker
                "lambda_mult": 0.7 
            }
        )

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
        
        # Step 2: Retrieve Broad Docs
        broad_docs = await self.retriever.ainvoke(standalone_query)
        
        # Step 2.5: RERANKING (Academic Enhancement)
        # Re-sort docs based on true semantic relevance to the query
        passages = [
            {"id": i, "text": doc.page_content, "meta": doc.metadata} 
            for i, doc in enumerate(broad_docs)
        ]
        
        rerank_request = RerankRequest(query=standalone_query, passages=passages)
        results = self.ranker.rerank(rerank_request)
        
        # Take Top 6 Reranked Docs
        top_results = results[:6]
        
        # Reconstruct Document objects
        from langchain_core.documents import Document
        docs = []
        for res in top_results:
             # Find original metadata if needed, but flashrank passes it back
             meta = res.get("meta", {})
             docs.append(Document(page_content=res["text"], metadata=meta))

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
