# RAG One - Document Q&A System

A Retrieval-Augmented Generation (RAG) system built with LangChain and Ollama, designed to run on WSL Oracle Linux while connecting to Ollama running on Windows.

## 🎯 Features

- **Semantic Document Search**: Index and search through your documents using AI-powered embeddings
- **Multiple Interfaces**: Both CLI and web-based UI for different use cases
- **Flexible Document Support**: Works with PDF, TXT, and DOCX files
- **Windows + WSL Integration**: Seamlessly connects to Ollama service running on Windows from WSL
- **Persistent Storage**: Vector embeddings stored locally for fast retrieval
- **Interactive Q&A**: Ask questions and get AI-generated answers based on your documents

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        RAG One System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐ │
│  │   Documents  │ --> │  Embeddings  │ -> │ Vector Store │ │
│  │  (PDF/TXT/   │     │  (Sentence   │    │  (ChromaDB)  │ │
│  │   DOCX)      │     │ Transformers)│    │              │ │
│  └──────────────┘     └──────────────┘    └──────────────┘ │
│                                                      ↓       │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐ │
│  │   User       │ --> │   LangChain  │ -> │   Ollama     │ │
│  │   Query      │     │   Retrieval  │    │   (Windows)  │ │
│  └──────────────┘     └──────────────┘    └──────────────┘ │
│         ↑                                          ↓         │
│  ┌──────────────┐                        ┌──────────────┐   │
│  │  CLI / Web   │ <--------------------- │   Response   │   │
│  │  Interface   │                        │              │   │
│  └──────────────┘                        └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### On Windows
1. **Ollama Installation**
   ```bash
   # Download from https://ollama.ai
   # Install and run Ollama
   
   # Pull a model (e.g., llama2)
   ollama pull llama2
   ```

2. **Verify Ollama is Running**
   ```bash
   # On Windows CMD or PowerShell
   curl http://localhost:11434/api/tags
   ```

### On WSL (Oracle Linux)
1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Git** (for cloning the repository)
   ```bash
   git --version
   ```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/samarthya/rag-one.git
cd rag-one
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (default settings should work for most cases)
nano .env
```

### 4. Test Ollama Connection from WSL
```bash
# Test if you can reach Ollama on Windows
curl http://localhost:11434/api/tags
```

If this doesn't work, you may need to use the Windows host IP address:
```bash
# Find Windows host IP (usually works automatically in WSL2)
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'

# Update OLLAMA_BASE_URL in .env if needed
# OLLAMA_BASE_URL=http://<windows-host-ip>:11434
```

## 📚 Usage

### Adding Documents

1. Place your documents in the `data/documents/` directory:
```bash
cp /path/to/your/document.pdf data/documents/
cp /path/to/your/document.txt data/documents/
```

Supported formats:
- PDF (`.pdf`)
- Text files (`.txt`)
- Word documents (`.docx`)

### CLI Interface

#### Index Documents
```bash
# Index all documents in data/documents/
python -m src.cli index

# Index documents from custom path
python -m src.cli index -d /path/to/documents
```

#### Query Documents (Single Question)
```bash
# Ask a single question
python -m src.cli query -q "What is RAG One?"

# With custom Ollama settings
python -m src.cli query -q "How do I set up the system?" --ollama-url http://localhost:11434 --ollama-model llama2
```

#### Interactive Query Mode
```bash
# Start interactive session
python -m src.cli query -i

# You'll get a prompt where you can ask multiple questions
# Type 'quit' or 'exit' to leave
```

#### System Information
```bash
# Check system status
python -m src.cli info
```

### Web Interface

Start the Streamlit web UI:
```bash
# Run the web app
streamlit run src/web_ui.py

# The app will open in your browser at http://localhost:8501
```

Features of the web UI:
- Chat-like interface for questions
- View source documents for each answer
- Configuration info in sidebar
- Clear chat history
- Responsive design

## 🔧 Configuration

Edit `.env` file to customize:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434    # Ollama server URL
OLLAMA_MODEL=llama2                       # Model to use

# Vector Store
VECTOR_STORE_TYPE=chroma                  # Vector store type
VECTOR_STORE_PATH=./data/vector_store    # Storage location

# Documents
DOCUMENTS_PATH=./data/documents          # Documents directory

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embedding model
```

## 🎓 Examples

### Example 1: Basic Setup
```bash
# 1. Add sample documents
cp myfile.pdf data/documents/

# 2. Index the documents
python -m src.cli index

# 3. Ask a question
python -m src.cli query -q "What is this document about?"
```

### Example 2: Interactive Session
```bash
# Start interactive mode
python -m src.cli query -i

# Now you can have a conversation:
You: What are the main topics in the documents?
Assistant: [AI response based on your documents]

You: Can you explain more about topic X?
Assistant: [Detailed explanation]

You: quit
```

### Example 3: Web UI
```bash
# 1. Make sure documents are indexed
python -m src.cli index

# 2. Start web interface
streamlit run src/web_ui.py

# 3. Open browser to http://localhost:8501
# 4. Start asking questions in the chat interface
```

## 🐛 Troubleshooting

### Ollama Connection Issues

**Problem**: Cannot connect to Ollama from WSL

**Solutions**:
1. Check if Ollama is running on Windows
2. Test with: `curl http://localhost:11434/api/tags`
3. If localhost doesn't work, find Windows host IP:
   ```bash
   cat /etc/resolv.conf | grep nameserver
   ```
4. Update `.env` with correct IP:
   ```
   OLLAMA_BASE_URL=http://<windows-ip>:11434
   ```
5. Check Windows Firewall settings

### Vector Store Not Found

**Problem**: "Vector store not found" error

**Solution**:
```bash
# Run the index command first
python -m src.cli index
```

### No Documents Found

**Problem**: "No documents found" when indexing

**Solution**:
1. Ensure documents are in `data/documents/`
2. Check file formats are supported (PDF, TXT, DOCX)
3. Verify file permissions

### Model Not Found

**Problem**: Ollama model not found

**Solution**:
```bash
# On Windows, pull the model
ollama pull llama2

# Verify model is available
ollama list
```

### Memory Issues

**Problem**: System runs out of memory

**Solutions**:
1. Use smaller documents
2. Reduce chunk size in `rag_engine.py`
3. Use a smaller embedding model
4. Close other applications

## 🔐 Security Notes

- The `.env` file contains configuration but no secrets in this setup
- Ollama runs locally on your Windows machine
- All data is stored locally
- No external API calls are made (except to local Ollama)

## 🛠️ Development

### Project Structure
```
rag-one/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── rag_engine.py        # Core RAG functionality
│   ├── cli.py               # CLI interface
│   └── web_ui.py            # Streamlit web interface
├── data/
│   ├── documents/           # Your documents go here
│   └── vector_store/        # Vector embeddings (generated)
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Running Tests
```bash
# Install test dependencies (if test suite exists)
pip install pytest pytest-cov

# Run tests
pytest
```

## 📝 License

This project is open source. Check the repository for license details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [Ollama](https://ollama.ai)
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- UI built with [Streamlit](https://streamlit.io)
