# RAG One - Usage Examples

This guide provides practical examples for using RAG One in different scenarios.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Advanced CLI Usage](#advanced-cli-usage)
- [Web Interface Examples](#web-interface-examples)
- [Custom Configuration](#custom-configuration)
- [Real-World Scenarios](#real-world-scenarios)

---

## Basic Usage

### Example 1: Getting Started with Sample Documents

```bash
# 1. The repository includes sample documents
ls data/documents/
# sample_doc1.txt  sample_doc2.txt

# 2. Index the documents
python -m src.cli index

# Output:
# Loading documents from: /path/to/data/documents
# Loaded 2 documents
# Creating vector store...
# Created vector store with 8 chunks
# Initializing QA chain...
# RAG engine ready!

# 3. Ask a question
python -m src.cli query -q "What is RAG One?"

# Output:
# Answer: RAG One is a Retrieval-Augmented Generation system...
# Sources:
#   1. sample_doc1.txt
```

### Example 2: Interactive Session

```bash
python -m src.cli query -i

# Interactive session:
You: What features does RAG One have?
Assistant: RAG One has several key features including document indexing 
and semantic search, integration with Ollama running on Windows...

You: How do I configure it for WSL?
Assistant: To configure RAG One for WSL, you need to ensure that...

You: quit
Goodbye!
```

---

## Advanced CLI Usage

### Example 3: Custom Document Path

```bash
# Index documents from a different location
python -m src.cli index -d /path/to/my/documents

# Query using that vector store
python -m src.cli query -q "Summary of documents?"
```

### Example 4: Different Ollama Model

```bash
# Use mistral model instead of llama2
python -m src.cli query \
  -q "Explain the main concepts" \
  --ollama-model mistral
```

### Example 5: Custom Ollama Server

```bash
# Connect to Ollama on a different machine
python -m src.cli query \
  -q "What does this document discuss?" \
  --ollama-url http://192.168.1.100:11434
```

### Example 6: System Information

```bash
python -m src.cli info

# Output:
# Documents path: /path/to/data/documents
# Ollama URL: http://localhost:11434
# Ollama model: llama2
# ✅ Vector store: exists
```

---

## Web Interface Examples

### Example 7: Basic Web UI Usage

```bash
# Start the web interface
streamlit run src/web_ui.py
```

Then in your browser at `http://localhost:8501`:

1. **First Question**: "What topics are covered in these documents?"
   - System retrieves relevant chunks
   - Displays answer with sources
   - Shows which documents were used

2. **Follow-up Question**: "Tell me more about [specific topic]"
   - Context from previous question helps
   - More detailed answer provided

3. **View Sources**: Click "View Sources" expander
   - See exact files used
   - Understand where information came from

### Example 8: Web UI Features

The web interface provides:
- Chat history (stays until you clear it)
- Source attribution for each answer
- Configuration display in sidebar
- Clear chat button
- Responsive design

---

## Custom Configuration

### Example 9: Environment Variables

Create or edit `.env`:

```bash
# Custom Ollama configuration
OLLAMA_BASE_URL=http://192.168.1.50:11434
OLLAMA_MODEL=mistral

# Custom vector store location
VECTOR_STORE_PATH=/mnt/data/my_vector_store

# Custom documents path
DOCUMENTS_PATH=/home/user/my_documents

# Different embedding model (smaller/faster)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Then use normally:
```bash
python -m src.cli index  # Uses settings from .env
python -m src.cli query -i
```

### Example 10: Programmatic Usage

Create your own Python script:

```python
from src.rag_engine import RAGEngine

# Initialize engine
engine = RAGEngine(
    ollama_url="http://localhost:11434",
    ollama_model="llama2"
)

# Setup from documents
engine.setup_from_documents("/path/to/docs")

# Query
result = engine.query("What is the main topic?")
print(result["answer"])

# Show sources
for doc in result["source_documents"]:
    print(f"Source: {doc.metadata['source']}")
```

---

## Real-World Scenarios

### Example 11: Research Paper Analysis

```bash
# 1. Add research papers
cp ~/Downloads/paper1.pdf data/documents/
cp ~/Downloads/paper2.pdf data/documents/
cp ~/Downloads/paper3.pdf data/documents/

# 2. Index papers
python -m src.cli index

# 3. Ask research questions
python -m src.cli query -i

You: What are the main findings across these papers?
You: What methodology did paper1 use?
You: Compare the approaches in paper1 and paper2
You: What are the limitations mentioned?
```

### Example 12: Technical Documentation Q&A

```bash
# 1. Add API documentation
cp -r ~/project/docs/*.md data/documents/

# 2. Index
python -m src.cli index

# 3. Query about API usage
python -m src.cli query -i

You: How do I authenticate with the API?
You: What are the rate limits?
You: Show me an example of making a POST request
You: What error codes can I expect?
```

### Example 13: Meeting Notes Search

```bash
# 1. Add meeting notes
cp ~/notes/meeting-*.txt data/documents/

# 2. Index
python -m src.cli index

# 3. Search through meetings
python -m src.cli query -q "What decisions were made about the project timeline?"
python -m src.cli query -q "Who was assigned to the frontend work?"
python -m src.cli query -q "What are the action items from last week?"
```

### Example 14: Code Documentation

```bash
# 1. Add code documentation files
cp ~/project/README.md data/documents/
cp ~/project/CONTRIBUTING.md data/documents/
cp ~/project/API.md data/documents/

# 2. Index
python -m src.cli index

# 3. Ask development questions
python -m src.cli query -i

You: How do I set up the development environment?
You: What's the process for submitting a pull request?
You: What are the coding standards?
```

### Example 15: Personal Knowledge Base

```bash
# 1. Organize various documents
mkdir -p data/documents/health
mkdir -p data/documents/finance
mkdir -p data/documents/learning

cp ~/documents/health/*.pdf data/documents/health/
cp ~/documents/finance/*.pdf data/documents/finance/
cp ~/documents/learning/*.txt data/documents/learning/

# 2. Index everything
python -m src.cli index -d data/documents

# 3. Query across all your knowledge
python -m src.cli query -i

You: What were my health checkup results?
You: What investments did I research last month?
You: Summary of the Python course notes
```

---

## Performance Tips

### Example 16: Optimizing for Large Document Sets

For large document collections:

1. **Batch processing**:
```bash
# Process documents in batches
python -m src.cli index -d data/documents/batch1
python -m src.cli index -d data/documents/batch2
```

2. **Monitor resource usage**:
```bash
# Check vector store size
du -sh data/vector_store/
```

3. **Use specific queries**:
```bash
# More specific = better results
python -m src.cli query -q "What is the specific feature X in document Y?"
# vs
python -m src.cli query -q "Tell me everything"
```

---

## Troubleshooting Examples

### Example 17: Testing Ollama Connection

```bash
# From WSL, test Ollama
curl http://localhost:11434/api/tags

# Should return JSON with available models
# If not, try Windows host IP:
cat /etc/resolv.conf | grep nameserver
# Then test with that IP
curl http://<windows-ip>:11434/api/tags
```

### Example 18: Re-indexing After Changes

```bash
# After adding new documents
ls data/documents/  # Verify new files are there

# Re-index (will replace old vector store)
python -m src.cli index

# Test with question about new content
python -m src.cli query -q "What's in the new document?"
```

---

## Best Practices

1. **Organize documents**: Keep related documents together
2. **Use descriptive filenames**: Helps with source attribution
3. **Re-index after changes**: Always re-index when adding documents
4. **Start specific**: Ask specific questions for best results
5. **Check sources**: Review source documents to verify answers
6. **Monitor performance**: Watch response times with large document sets

---

## Next Steps

- Try these examples with your own documents
- Experiment with different models (mistral, codellama, etc.)
- Customize the system for your workflow
- Integrate into your development process

For more information, see:
- [README.md](README.md) - Overview
- [README_DETAILED.md](README_DETAILED.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
