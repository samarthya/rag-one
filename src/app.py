"""
Personal Assistant Web Interface
A Streamlit app for interacting with your RAG-powered assistant
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path

import streamlit as st

import fix_sqlite  # SQLite fix must be first!
from config import DOCUMENTS_DIR
from rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="My Personal Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_rag_engine():
    """
    Load the RAG engine.
    @st.cache_resource ensures it's only loaded once and shared across sessions.
    This is important for performance!
    """
    return RAGEngine()


def save_uploaded_file(uploaded_file) -> bool:
    """
    Save an uploaded file to the documents directory.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = DOCUMENTS_DIR / uploaded_file.name

        # Check if file already exists
        if file_path.exists():
            st.warning(f"File '{uploaded_file.name}' already exists. Overwriting...")

        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return True

    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False


def get_document_list():
    """Get list of documents in the documents directory"""
    supported_extensions = [".pdf", ".txt", ".docx", ".doc", ".xlsx", ".xls"]
    files = [
        f
        for f in DOCUMENTS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    return sorted(files, key=lambda x: x.name)


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sidebar():
    """Render the sidebar with document management"""
    with st.sidebar:
        st.title("📚 Knowledge Base")

        # Get RAG engine stats
        rag = load_rag_engine()
        stats = rag.get_stats()

        # Display stats
        st.metric("Total Chunks", stats["total_chunks"])

        st.divider()

        # Document upload section
        st.subheader("➕ Add Documents")

        uploaded_files = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "docx", "doc", "xlsx", "xls"],
            accept_multiple_files=True,
            help="Upload PDF, Word, Excel, or text files",
        )

        if uploaded_files:
            if st.button("📤 Process Uploaded Files", type="primary"):
                with st.spinner("Saving and processing files..."):
                    # Save files
                    saved_count = 0
                    for uploaded_file in uploaded_files:
                        if save_uploaded_file(uploaded_file):
                            saved_count += 1

                    if saved_count > 0:
                        # Process documents
                        stats = rag.process_documents()

                        # Clear cache to reload RAG engine
                        st.cache_resource.clear()

                        st.success(
                            f"""
                        ✅ Processing complete!
                        - Files processed: {stats['files_processed']}
                        - New chunks created: {stats['total_chunks']}
                        """
                        )
                        st.rerun()

        st.divider()

        # List existing documents
        st.subheader("📄 Current Documents")

        documents = get_document_list()

        if documents:
            st.write(f"*{len(documents)} document(s)*")

            for doc in documents:
                col1, col2 = st.columns([3, 1])

                with col1:
                    # File icon based on type
                    icon = {
                        ".pdf": "📕",
                        ".txt": "📝",
                        ".docx": "📘",
                        ".doc": "📘",
                        ".xlsx": "📊",
                        ".xls": "📊",
                    }.get(doc.suffix.lower(), "📄")

                    st.write(f"{icon} `{doc.name}`")
                    st.caption(format_file_size(doc.stat().st_size))

                with col2:
                    if st.button("🗑️", key=f"delete_{doc.name}"):
                        try:
                            doc.unlink()
                            st.success(f"Deleted {doc.name}")
                            st.info(
                                "⚠️ Please reprocess documents to update the knowledge base"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.info("No documents yet. Upload some to get started!")

        st.divider()

        # Reprocess all documents button
        if documents:
            if st.button(
                "🔄 Reprocess All Documents", help="Rebuild the entire knowledge base"
            ):
                with st.spinner("Reprocessing all documents..."):
                    stats = rag.process_documents()
                    st.cache_resource.clear()
                    st.success(
                        f"✅ Processed {stats['files_processed']} files into {stats['total_chunks']} chunks"
                    )
                    st.rerun()


def main():
    """Main application"""

    # Render sidebar
    sidebar()

    # Main chat interface
    st.title("🤖 My Personal Assistant")
    st.caption("Ask me anything about your documents!")

    # Initialize RAG engine
    rag = load_rag_engine()

    # Check if knowledge base is empty
    stats = rag.get_stats()
    if stats["total_chunks"] == 0:
        st.warning(
            "⚠️ No documents in knowledge base. Please upload documents using the sidebar."
        )
        return

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.caption(f"• {source}")

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get answer from RAG engine
                result = rag.ask(prompt)

                # Display answer
                st.markdown(result["answer"])

                # Display sources
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        for source in result["sources"]:
                            st.caption(f"• {source}")

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    }
                )

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
