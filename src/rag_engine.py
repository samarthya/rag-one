"""rag_engine.py
Central orchestration layer that performs Retrieval-Augmented Generation (RAG).

Purpose
    Couples a retrieval component (vector store + retriever) with a language
    model (LLM) to answer user queries using only indexed document context.

High-Level Flow
    1. User calls `ask(question)`.
    2. Engine checks that documents have been processed (vector store populated).
    3. Retriever fetches top-K relevant chunks (semantic similarity search).
    4. Prompt template is filled with system instructions, retrieved context, and question.
    5. LLM generates grounded answer; source documents returned for transparency.

Core Components
    - DocumentProcessor: handles ingest, chunking, embedding, persistence.
    - Vector Store (Chroma): provides similarity search; converted to a retriever.
    - PromptTemplate: defines structure and guardrails for generation.
    - RetrievalQA Chain (LangChain): maps query → retrieval → prompt assembly → LLM call.

Design Decisions
    - Uses "stuff" chain type: all retrieved chunks concatenated; simple & effective for
      small knowledge bases. Consider map-reduce or refine for larger corpora.
    - Separation of concerns: ingestion/indexing lives in `document_processor.py`; the
      engine focuses only on retrieval + answer synthesis.
    - Defensive initialization: QA chain creation wrapped so failures (e.g., missing vector
      store) do not crash the engine; `ask` returns actionable guidance instead.

Public API
    - RAGEngine.ask(question) -> Dict[str, Any]
        Returns: {
            'answer': str,
            'sources': List[str],    # human-readable source identifiers
            'context': List[str]     # raw text chunks used
        }
    - RAGEngine.process_documents() -> Dict[str, int]
        Delegates to DocumentProcessor to (re)index all documents.
    - RAGEngine.get_stats() -> Dict[str, Any]
        Lightweight health info (e.g., total_chunks).

Error Handling & Safeguards
    - If no documents are indexed, `ask` returns a guidance message instead of calling LLM.
    - If QA chain failed to initialize (vector store absent), `ask` explains corrective action.
    - Exceptions during answer generation are caught and returned as error strings—keeps UI stable.

Extensibility
    - Swap `chain_type` in `_create_qa_chain` for more advanced prompt assembly strategies.
    - Add answer post-processing (citation formatting, summarization) after generation in `ask`.
    - Integrate filtering (e.g., metadata constraints) by customizing retriever search kwargs.

Example Usage
    >>> engine = RAGEngine()
    >>> engine.process_documents()  # index documents first (once or after updates)
    >>> response = engine.ask("Explain vector embeddings")
    >>> print(response['answer'])
    >>> print(response['sources'])

Configuration
    All tunable parameters (model names, TOP_K_RESULTS, system prompt) reside in `config.py`.
    Adjust there; re-index if chunking or embedding settings change.

Notes
    For larger corpora, consider:
        • Limiting context length (truncate long chunks or apply ranking heuristics).
        • Diversifying retrieval (hybrid sparse + dense search).
        • Adding caching for frequent queries.
"""

import logging
from typing import Dict, List, Optional, Any

from langchain_classic.chains import RetrievalQA  # UPDATED
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

import fix_sqlite  # SQLite fix must be first!
from document_processor import DocumentProcessor
from conversation_memory import ConversationMemory

from config import (
    OLLAMA_BASE_URL,
    LLM_MODEL,
    REASONING_MODEL,
    TOP_K_RESULTS,
    SYSTEM_PROMPT,
    DATA_DIR,  # Add this to config.py if not there
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    The RAG Engine combines retrieval and generation.

    Think of it as:
    - Librarian (finds relevant books)
    - Expert (reads and answers your question)
    """

    def __init__(self, conversation_id: Optional[str] = None):
        """Initialize the RAG Engine"""
        logger.info("Initializing RAG Engine with conversation memory...")

        # Initialize document processor (handles retrieval)
        self.doc_processor = DocumentProcessor()

        # Initialize LLM (handles generation)
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,  # Controls randomness (0=deterministic, 1=creative)
        )

        # Reasoning LLM for complex tasks
        self.reasoning_llm = Ollama(
            model=REASONING_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,
        )

        memory_dir = DATA_DIR / "conversations"
        self.memory = ConversationMemory(
            max_history=5,  # Keep last 5 exchanges in context
            persist_dir=memory_dir
        )

        self.conversation_id = conversation_id
        
        # Load previous conversation if ID provided
        if conversation_id:
            try:
                self.memory.load_conversation(f"{conversation_id}.json")
                logger.info(f"Loaded conversation: {conversation_id}")
            except FileNotFoundError:
                logger.info(f"Starting new conversation: {conversation_id}")
        
        # Create prompt template with memory
        self.prompt_template = self._create_prompt_template()

        logger.info(" RAG Engine ready!")

    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create prompt template that includes conversation history.
        """
        template = """
{system_prompt}

{conversation_history}

Context from documents:
---
{context}
---

Current Question: {question}

Instructions:
1. Consider the conversation history above
2. Use the document context provided
3. If the question refers to previous conversation, use that context
4. If you don't know, say so clearly

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question", "conversation_history"],
            partial_variables={"system_prompt": SYSTEM_PROMPT}
        )

    def _create_qa_chain(self):
        """
        Create the Question-Answering chain.

        This chain orchestrates:
        1. Retrieval (get relevant docs)
        2. Prompt building (insert into template)
        3. LLM call (generate answer)
        """
        # Convert vector store to retriever
        vectorstore = self.doc_processor.vectorstore
        if vectorstore is None:
            # Defensive guard so static analysis and runtime are safe
            logger.error("Vector store not initialized; cannot create retriever.")
            raise RuntimeError("Vector store is not initialized")

        retriever = vectorstore.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )

        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # "stuff" = put all context in one prompt
            retriever=retriever,
            return_source_documents=True,  # Return which docs were used
            chain_type_kwargs={"prompt": self.prompt_template},
        )

        return qa_chain

    def _process_answer(self, raw_answer: str, use_reasoning: bool) -> tuple[str, Optional[str]]:
        """
        Process the raw answer from LLM.
        Extracts thinking process if using DeepSeek-R1.
        
        Args:
            raw_answer: Raw response from LLM
            use_reasoning: Whether reasoning model was used
            
        Returns:
            Tuple of (clean_answer, reasoning_process)
        """
        if not use_reasoning:
            # Standard model - no thinking tags
            return raw_answer, None
        
        # DeepSeek-R1 may include <thinking> tags
        if "<thinking>" in raw_answer and "</thinking>" in raw_answer:
            try:
                # Extract thinking process
                thinking_start = raw_answer.find("<thinking>") + len("<thinking>")
                thinking_end = raw_answer.find("</thinking>")
                reasoning = raw_answer[thinking_start:thinking_end].strip()
                
                # Extract final answer (after </thinking>)
                answer = raw_answer[thinking_end + len("</thinking>"):].strip()
                
                return answer, reasoning
            except Exception as e:
                logger.warning(f"Error parsing thinking tags: {e}")
                return raw_answer, None
        else:
            # No thinking tags found
            return raw_answer, None
        
    def ask(self, question: str, use_memory: bool = True, use_reasoning: bool = False) -> Dict[str, Any]:
        """
        Ask a question with conversational memory and optional reasoning mode.
        
        Args:
            question: Your question
            use_memory: Whether to include conversation history in context
            use_reasoning: Whether to use DeepSeek-R1 for deeper analysis (slower but more detailed)
            
        Returns:
            Dictionary with answer, sources, context, and optionally reasoning
        """
        logger.info(f"Question: {question} (Reasoning mode: {use_reasoning})")
        
        # Check if vector store has documents
        stats = self.doc_processor.get_stats()
        if stats['total_chunks'] == 0:
            return {
                'answer': "No documents have been processed yet.",
                'sources': [],
                'context': [],
                'reasoning': None
            }
        
        try:
            # Get conversation history
            conversation_history = ""
            if use_memory and self.memory.messages:
                conversation_history = self.memory.get_context_string(last_n=3)
            
            # Retrieve relevant documents
            retrieved_docs = self.doc_processor.search(question, k=TOP_K_RESULTS)
            
            # Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Build the full prompt
            prompt = self.prompt_template.format(
                context=context,
                question=question,
                conversation_history=conversation_history
            )
            
            # Select LLM based on reasoning flag
            selected_llm = self.reasoning_llm if use_reasoning else self.llm
            
            # Generate answer
            raw_answer = selected_llm.invoke(prompt)
            
            # Process answer (extract thinking if present)
            answer, reasoning = self._process_answer(raw_answer, use_reasoning)
            
            # Format sources
            sources = self._format_sources(retrieved_docs)
            
            # Add to memory
            self.memory.add_message('user', question)
            self.memory.add_message('assistant', answer, {'sources': sources})
            
            # Auto-save if conversation_id is set
            if self.conversation_id:
                self.memory.save_conversation(f"{self.conversation_id}.json")
            
            logger.info("✓ Answer generated with conversational context")
            
            return {
                'answer': answer,
                'sources': sources,
                'context': [doc.page_content for doc in retrieved_docs],
                'reasoning': reasoning  # NEW: DeepSeek's thinking process
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                'answer': f"Error: {str(e)}",
                'sources': [],
                'context': [],
                'reasoning': None
            }
    
    def get_conversation_summary(self) -> str:
        """Get summary of current conversation."""
        return self.memory.get_conversation_summary()
    
    def clear_conversation(self):
        """Clear current conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def save_conversation(self, filename: Optional[str] = None):
        """
        Save current conversation.
        
        Args:
            filename: Optional custom filename (default uses conversation_id)
        """
        if not filename:
            filename = f"{self.conversation_id or 'conversation'}.json"
        
        self.memory.save_conversation(filename)
        logger.info(f"Conversation saved: {filename}")

    def _format_sources(self, documents: List[Document]) -> List[str]:
        """Format source documents into readable references."""
        sources = []
        seen = set()
        
        for doc in documents:
            source = doc.metadata.get('source', 'Unknown')
            
            if 'page' in doc.metadata:
                source = f"{source} (page {doc.metadata['page']})"
            
            if 'sheet' in doc.metadata:
                source = f"{source} (sheet: {doc.metadata['sheet']})"
            
            if source not in seen:
                sources.append(source)
                seen.add(source)
        
        return sources

    def process_documents(self) -> Dict[str, int]:
        """
        Process all documents in the documents folder.
        Convenience method that calls the document processor.

        Returns:
            Statistics about processed documents
        """
        return self.doc_processor.process_all_documents()

    def get_stats(self) -> Dict:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary with stats
        """
        return self.doc_processor.get_stats()


# Test function
if __name__ == "__main__":
    """
    Test the RAG Engine
    """
    print("=" * 60)
    print("Testing RAG Engine")
    print("=" * 60)

    # Initialize
    rag = RAGEngine()

    # Get stats
    stats = rag.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")

    # Test questions
    test_questions = [
        "What is my name?",
        "Where do I work?",
        "What am I studying?",
    ]

    print("\n" + "=" * 60)
    print("Testing Questions")
    print("=" * 60)

    for question in test_questions:
        print(f"\n❓ {question}")
        print("-" * 60)

        result = rag.ask(question)

        print(f"💬 Answer: {result['answer']}")

        if result["sources"]:
            print(f"\n📚 Sources: {', '.join(result['sources'])}")

        print()
