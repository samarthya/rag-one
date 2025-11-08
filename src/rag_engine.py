"""Core RAG engine using LangChain and Ollama."""

import os
from pathlib import Path
from typing import List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    VECTOR_STORE_PATH,
    EMBEDDING_MODEL,
    DOCUMENTS_PATH,
)


class RAGEngine:
    """RAG engine for document Q&A using LangChain and Ollama."""

    def __init__(
        self,
        ollama_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        vector_store_path: Optional[str] = None,
    ):
        """Initialize the RAG engine.

        Args:
            ollama_url: Ollama server URL (default: from config)
            ollama_model: Ollama model name (default: from config)
            vector_store_path: Path to vector store (default: from config)
        """
        self.ollama_url = ollama_url or OLLAMA_BASE_URL
        self.ollama_model = ollama_model or OLLAMA_MODEL
        self.vector_store_path = vector_store_path or VECTOR_STORE_PATH

        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )

        # Initialize LLM
        self.llm = Ollama(
            base_url=self.ollama_url,
            model=self.ollama_model,
        )

        # Vector store (loaded on demand)
        self.vector_store = None
        self.qa_chain = None

    def load_documents(self, documents_path: str) -> List:
        """Load documents from a directory.

        Args:
            documents_path: Path to documents directory

        Returns:
            List of loaded documents
        """
        documents = []
        doc_path = Path(documents_path)

        if not doc_path.exists():
            raise ValueError(f"Documents path does not exist: {documents_path}")

        # Load text files
        try:
            txt_loader = DirectoryLoader(
                documents_path,
                glob="**/*.txt",
                loader_cls=TextLoader,
                show_progress=True,
            )
            documents.extend(txt_loader.load())
        except Exception as e:
            print(f"Warning: Error loading text files: {e}")

        # Load PDF files
        try:
            pdf_files = list(doc_path.glob("**/*.pdf"))
            for pdf_file in pdf_files:
                try:
                    pdf_loader = PyPDFLoader(str(pdf_file))
                    documents.extend(pdf_loader.load())
                except Exception as e:
                    print(f"Warning: Error loading {pdf_file}: {e}")
        except Exception as e:
            print(f"Warning: Error loading PDF files: {e}")

        # Load DOCX files
        try:
            docx_files = list(doc_path.glob("**/*.docx"))
            for docx_file in docx_files:
                try:
                    docx_loader = Docx2txtLoader(str(docx_file))
                    documents.extend(docx_loader.load())
                except Exception as e:
                    print(f"Warning: Error loading {docx_file}: {e}")
        except Exception as e:
            print(f"Warning: Error loading DOCX files: {e}")

        return documents

    def split_documents(self, documents: List, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
        """Split documents into chunks.

        Args:
            documents: List of documents to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    def create_vector_store(self, documents: List) -> None:
        """Create a vector store from documents.

        Args:
            documents: List of documents to index
        """
        # Split documents
        chunks = self.split_documents(documents)

        if not chunks:
            raise ValueError("No document chunks to index")

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.vector_store_path,
        )

        print(f"Created vector store with {len(chunks)} chunks")

    def load_vector_store(self) -> None:
        """Load existing vector store."""
        if not os.path.exists(self.vector_store_path):
            raise ValueError(f"Vector store does not exist at: {self.vector_store_path}")

        self.vector_store = Chroma(
            persist_directory=self.vector_store_path,
            embedding_function=self.embeddings,
        )

    def initialize_qa_chain(self) -> None:
        """Initialize the QA chain."""
        if self.vector_store is None:
            raise ValueError("Vector store not loaded. Call load_vector_store() or create_vector_store() first.")

        # Create custom prompt template
        prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Answer: """

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"],
        )

        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
        )

    def query(self, question: str) -> dict:
        """Query the RAG system.

        Args:
            question: Question to ask

        Returns:
            Dictionary with answer and source documents
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call initialize_qa_chain() first.")

        result = self.qa_chain({"query": question})

        return {
            "answer": result["result"],
            "source_documents": result.get("source_documents", []),
        }

    def setup_from_documents(self, documents_path: Optional[str] = None) -> None:
        """Complete setup: load documents, create vector store, and initialize QA chain.

        Args:
            documents_path: Path to documents (default: from config)
        """
        doc_path = documents_path or DOCUMENTS_PATH

        print(f"Loading documents from: {doc_path}")
        documents = self.load_documents(doc_path)

        if not documents:
            raise ValueError(f"No documents found in: {doc_path}")

        print(f"Loaded {len(documents)} documents")

        print("Creating vector store...")
        self.create_vector_store(documents)

        print("Initializing QA chain...")
        self.initialize_qa_chain()

        print("RAG engine ready!")

    def setup_from_existing_store(self) -> None:
        """Setup using existing vector store."""
        print("Loading existing vector store...")
        self.load_vector_store()

        print("Initializing QA chain...")
        self.initialize_qa_chain()

        print("RAG engine ready!")
