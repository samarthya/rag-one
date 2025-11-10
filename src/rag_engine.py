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
from config import LLM_MODEL, OLLAMA_BASE_URL, SYSTEM_PROMPT, TOP_K_RESULTS
from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    The RAG Engine combines retrieval and generation.

    Think of it as:
    - Librarian (finds relevant books)
    - Expert (reads and answers your question)
    """

    def __init__(self):
        """Initialize the RAG Engine"""
        logger.info("Initializing RAG Engine...")

        # Initialize document processor (handles retrieval)
        self.doc_processor = DocumentProcessor()

        # Initialize LLM (handles generation)
        self.llm = Ollama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,  # Controls randomness (0=deterministic, 1=creative)
        )

        # Create the prompt template
        self.prompt_template = self._create_prompt_template()

        # Create the QA chain (may fail if vector store isn't ready)
        self.qa_chain = None
        try:
            self.qa_chain = self._create_qa_chain()
        except Exception as e:
            logger.error(f"Failed to create QA chain: {e}")
            self.qa_chain = None

        logger.info("✓ RAG Engine ready!")

    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create the prompt template for the LLM.

        This is CRUCIAL - it tells the LLM:
        - What role to play
        - What context it has
        - What question to answer
        - How to behave
        """
        template = """
{system_prompt}

Context from documents:
---
{context}
---

Question: {question}

Answer based on the context above. If the answer is not in the context, say "I don't have that information in the documents."

Answer:"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"],
            partial_variables={"system_prompt": SYSTEM_PROMPT},
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

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get an answer!

        This is the main function you'll use.

        Args:
            question: Your question

        Returns:
            Dictionary with:
            - answer: The LLM's response
            - sources: Which documents were used
            - context: The actual text chunks retrieved
        """
        logger.info(f"Question: {question}")

        # Check if vector store has documents
        stats = self.doc_processor.get_stats()
        if stats["total_chunks"] == 0:
            return {
                "answer": "No documents have been processed yet. Please add documents to the data/documents folder and process them first.",
                "sources": [],
                "context": [],
            }

        try:
            # Run the QA chain
            if self.qa_chain is None:
                return {
                    'answer': "The QA chain is not available yet. Please process documents first or check vector store initialization.",
                    'sources': [],
                    'context': []
                }

            result = self.qa_chain.invoke({"query": question})

            # Extract results
            answer = result["result"]
            source_docs = result["source_documents"]

            # Format sources
            sources = self._format_sources(source_docs)

            # Get context text
            context = [doc.page_content for doc in source_docs]

            logger.info("✓ Answer generated")

            return {"answer": answer, "sources": sources, "context": context}

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {"answer": f"Error: {str(e)}", "sources": [], "context": []}

    def _format_sources(self, documents: List[Document]) -> List[str]:
        """
        Format source documents into readable references.

        Args:
            documents: List of source documents

        Returns:
            List of formatted source strings
        """
        sources = []
        seen = set()  # Avoid duplicates

        for doc in documents:
            source = doc.metadata.get("source", "Unknown")

            # Add page number if available
            if "page" in doc.metadata:
                source = f"{source} (page {doc.metadata['page']})"

            # Add sheet name for Excel
            if "sheet" in doc.metadata:
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
