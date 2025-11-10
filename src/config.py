"""config.py
Central configuration for the RAG Personal Assistant.

What & Why:
	Instead of scattering magic numbers and environment-specific details
	across the codebase, we centralize them here to make the retrieval +
	generation pipeline easier to reason about and tune.

Sections:
	PROJECT PATHS
		Absolute paths for data and vector store persistence. Persisting
		the Chroma index lets us avoid recomputing embeddings each run.

	OLLAMA CONFIGURATION (WSL-friendly)
		When developing inside WSL but running Ollama on Windows, the
		base URL must point to the Windows host IP. This allows embedding
		and LLM calls to work seamlessly from Linux tooling.

	MODEL CHOICES
		LLM_MODEL: main language model used for generation.
		EMBEDDING_MODEL: separate, typically smaller model optimized for
		producing semantic embeddings for chunk similarity searches.

	RAG CONFIGURATION
		CHUNK_SIZE / CHUNK_OVERLAP: tune granularity vs. context cohesion.
		Smaller chunks improve precision; overlap prevents hard context cuts.
		TOP_K_RESULTS: trade off coverage vs. prompt length.
		SIMILARITY_THRESHOLD: optional guardrail to filter weak matches;
		you can apply this manually before building prompts.

	SYSTEM PROMPT
		A stable instruction block injected into every retrieval-augmented
		prompt. Keeps responses grounded and honest when context is absent.

Tuning guidance:
	- If answers miss relevant info, increase TOP_K_RESULTS or CHUNK_SIZE.
	- If answers include unrelated fluff, decrease TOP_K_RESULTS or tighten
	  SIMILARITY_THRESHOLD filtering logic where retrieval occurs.
	- Adjust CHUNK_OVERLAP if sentences straddle chunk boundaries.

All values here are safe defaults for a small personal knowledge base.
Modify them iteratively and re-index documents as needed.
"""

import os
from pathlib import Path

# ============================================
# PROJECT PATHS
# ============================================
BASE_DIR = Path(__file__).parent.parent  # Root of the project (src/..) -> used to derive data paths

DATA_DIR = BASE_DIR / "data"              # Top-level data directory
DOCUMENTS_DIR = DATA_DIR / "documents"    # Raw source documents to ingest
VECTORSTORE_DIR = DATA_DIR / "vectorstore" # Persistent Chroma vector store (embeddings index)

# Create directories if they don't exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# OLLAMA CONFIGURATION
# ============================================
# WSL needs to connect to Windows Ollama.
# Find your Windows IP inside WSL:
#   ip route show | grep default | awk '{print $3}'
WINDOWS_IP = "172.22.112.1"  # Replace with your live host IP if it changes (DHCP can reassign)
OLLAMA_BASE_URL = f"http://{WINDOWS_IP}:11434"  # Base endpoint for both LLM and embedding calls

# Your LLM model
LLM_MODEL = "gpt-oss:20b"  # Main generation model (swap for smaller/faster if latency is high)

# Embedding model (we'll download this via Ollama)
EMBEDDING_MODEL = "nomic-embed-text"  # Embedding model optimized for semantic similarity search

# ============================================
# RAG CONFIGURATION
# ============================================
# Chunking settings
CHUNK_SIZE = 1000      # Target max characters per chunk (precision vs. context tradeoff)
CHUNK_OVERLAP = 200    # Characters repeated between adjacent chunks to preserve continuity

# Retrieval settings
TOP_K_RESULTS = 4           # Number of top chunks retrieved per query; raise for broader context
SIMILARITY_THRESHOLD = 0.7  # Optional min similarity (0-1); apply in retrieval code if filtering

# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """You are a helpful personal assistant.
Answer questions strictly using the provided document context.
If the answer is not present, say you don't have that information.
Prefer concise, accurate responses; avoid speculation."""
