# RAG One - Quick Start Guide

Get up and running with RAG One in 5 minutes!

## Step 1: Prerequisites Check ✅

### On Windows
- [ ] Ollama installed (download from https://ollama.ai)
- [ ] Ollama service running
- [ ] At least one model pulled (e.g., `ollama pull llama2`)

### On WSL
- [ ] Python 3.8+ installed
- [ ] Git installed

## Step 2: Installation 📦

```bash
# Clone and enter directory
git clone https://github.com/samarthya/rag-one.git
cd rag-one

# Run automated setup
./setup.sh
```

The setup script will:
- Create a virtual environment
- Install all dependencies
- Create configuration files
- Test Ollama connection
- Set up directories

## Step 3: Prepare Documents 📄

Add your documents to the `data/documents/` folder:

```bash
# Example: Copy your documents
cp ~/my-document.pdf data/documents/
cp ~/my-notes.txt data/documents/
```

Supported formats: PDF, TXT, DOCX

## Step 4: Index Your Documents 🔍

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Index all documents
python -m src.cli index
```

This will:
- Load all documents
- Create embeddings
- Build the vector store
- Usually takes 30-60 seconds for a few documents

## Step 5: Start Asking Questions! 💬

### Option A: CLI (Interactive Mode)

```bash
python -m src.cli query -i
```

Example session:
```
You: What are the main topics in my documents?
Assistant: [AI provides answer with sources]

You: Tell me more about topic X
Assistant: [Detailed explanation]

You: quit
```

### Option B: CLI (Single Question)

```bash
python -m src.cli query -q "What is this document about?"
```

### Option C: Web Interface

```bash
streamlit run src/web_ui.py
```

Then open your browser to `http://localhost:8501`

Features:
- Chat-like interface
- See source documents
- Clear conversation history
- User-friendly UI

## Common Commands 🛠️

### Check System Status
```bash
python -m src.cli info
```

### Re-index Documents (after adding new ones)
```bash
python -m src.cli index
```

### Use Different Model
```bash
python -m src.cli query -q "My question" --ollama-model mistral
```

### Custom Ollama URL
```bash
python -m src.cli query -q "My question" --ollama-url http://192.168.1.100:11434
```

## Troubleshooting 🔧

### "Cannot connect to Ollama"

1. Check Ollama is running on Windows:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. If that fails, find Windows host IP:
   ```bash
   cat /etc/resolv.conf | grep nameserver
   ```

3. Update `.env`:
   ```
   OLLAMA_BASE_URL=http://<your-windows-ip>:11434
   ```

### "Vector store not found"

Run the index command first:
```bash
python -m src.cli index
```

### "No documents found"

Make sure documents are in `data/documents/`:
```bash
ls -la data/documents/
```

## Next Steps 🚀

Now you're ready to:
- Add more documents
- Try different queries
- Explore the web interface
- Experiment with different models

For detailed documentation, see [README_DETAILED.md](README_DETAILED.md)

## Tips 💡

1. **Start small**: Index a few documents first to test
2. **Use descriptive questions**: The more specific, the better the answer
3. **Check sources**: The system shows which documents were used
4. **Interactive mode**: Great for exploratory conversations
5. **Web UI**: Best for longer sessions and better UX

Enjoy using RAG One! 🎉
