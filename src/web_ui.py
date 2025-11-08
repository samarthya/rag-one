"""Streamlit web UI for RAG One."""

import streamlit as st
import os
from pathlib import Path

from src.rag_engine import RAGEngine
from src.config import (
    DOCUMENTS_PATH,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    VECTOR_STORE_DIR,
)


# Page config
st.set_page_config(
    page_title="RAG One - Document Q&A",
    page_icon="🤖",
    layout="wide",
)


@st.cache_resource
def load_rag_engine():
    """Load and cache the RAG engine."""
    try:
        engine = RAGEngine(
            ollama_url=OLLAMA_BASE_URL,
            ollama_model=OLLAMA_MODEL,
        )
        
        # Check if vector store exists
        if VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir()):
            engine.setup_from_existing_store()
            return engine, None
        else:
            return None, "Vector store not found. Please index documents first."
    except Exception as e:
        return None, f"Error loading RAG engine: {str(e)}"


def main():
    """Main Streamlit app."""
    st.title("🤖 RAG One - Document Q&A System")
    st.markdown("Ask questions about your documents using AI powered by Ollama")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"**Ollama URL:** {OLLAMA_BASE_URL}")
        st.info(f"**Model:** {OLLAMA_MODEL}")
        st.info(f"**Documents:** {DOCUMENTS_PATH}")
        
        st.markdown("---")
        st.header("📚 Setup")
        
        # Check vector store status
        if VECTOR_STORE_DIR.exists() and any(VECTOR_STORE_DIR.iterdir()):
            st.success("✅ Vector store ready")
        else:
            st.warning("⚠️ Vector store not found")
            st.markdown("""
            **To set up:**
            1. Add documents to `data/documents/`
            2. Run: `python -m src.cli index`
            3. Refresh this page
            """)

        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This RAG (Retrieval-Augmented Generation) system:
        - Uses LangChain for orchestration
        - Connects to Ollama (Windows service)
        - Works on WSL Oracle Linux
        - Provides semantic search over your documents
        """)

    # Load RAG engine
    engine, error = load_rag_engine()

    if error:
        st.error(error)
        st.markdown("""
        ### Getting Started
        1. Place your documents (PDF, TXT, DOCX) in `data/documents/`
        2. Run the indexing command:
           ```bash
           python -m src.cli index
           ```
        3. Refresh this page
        """)
        return

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.text(f"{i}. {source}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = engine.query(prompt)
                    answer = result["answer"]
                    sources = [
                        Path(doc.metadata.get("source", "Unknown")).name
                        for doc in result.get("source_documents", [])[:3]
                    ]

                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 View Sources"):
                            for i, source in enumerate(sources, 1):
                                st.text(f"{i}. {source}")

                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })

    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
