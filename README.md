# RAG One

Building a local RAG (Retrieval-Augmented Generation) agent using LangChain and Ollama for WSL Oracle Linux with Windows-hosted Ollama service.

## 🚀 Quick Start

### Prerequisites
- Windows with Ollama installed and running (https://ollama.ai)
- WSL (Oracle Linux or Ubuntu)
- Python 3.8+

### Installation
```bash
# Clone the repository
git clone https://github.com/samarthya/rag-one.git
cd rag-one

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### Basic Usage

#### 1. Add Your Documents
```bash
# Place your documents (PDF, TXT, DOCX) in the documents folder
cp /path/to/your/document.pdf data/documents/
```

#### 2. Index Documents
```bash
python -m src.cli index
```

#### 3. Query via CLI
```bash
# Single question
python -m src.cli query -q "What is this about?"

# Interactive mode
python -m src.cli query -i
```

#### 4. Or Use Web UI
```bash
streamlit run src/web_ui.py
```

## 📚 Documentation

See [README_DETAILED.md](README_DETAILED.md) for:
- Complete setup guide
- Windows + WSL integration details
- Troubleshooting
- Advanced configuration
- Examples

## ✨ Features

- 🔍 Semantic search across multiple documents
- 💬 Interactive CLI and Web UI
- 🔗 Seamless Windows Ollama integration from WSL
- 📄 Support for PDF, TXT, and DOCX files
- 🎯 RAG-based question answering with source attribution
- ⚡ Fast vector-based retrieval with ChromaDB

## 🏗️ Architecture

```
Documents → Embeddings → Vector Store → Retrieval → Ollama (Windows) → Answer
```

## 🛠️ Tech Stack

- **LangChain**: RAG orchestration
- **Ollama**: LLM inference (running on Windows)
- **ChromaDB**: Vector storage
- **Streamlit**: Web interface
- **Click & Rich**: CLI interface

## 📋 Requirements

- Python 3.8+
- Ollama service running on Windows
- 4GB+ RAM recommended
- WSL2 with network access to Windows host

## 🎯 Use Cases

- Technical documentation Q&A
- Research paper analysis
- Knowledge base queries
- Document summarization
- Information extraction

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📝 License

Open source - see repository for details.
