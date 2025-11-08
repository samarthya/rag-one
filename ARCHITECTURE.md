# RAG One - Architecture

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐              ┌──────────────┐                │
│   │   CLI Tool   │              │   Web App    │                │
│   │  (Click +    │              │  (Streamlit) │                │
│   │    Rich)     │              │              │                │
│   └──────┬───────┘              └──────┬───────┘                │
│          │                             │                         │
│          └──────────────┬──────────────┘                         │
│                         │                                        │
└─────────────────────────┼────────────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────────────┐
│                         │         Core Layer                     │
├─────────────────────────┼────────────────────────────────────────┤
│                         ↓                                        │
│              ┌────────────────────┐                              │
│              │    RAG Engine      │                              │
│              │  (rag_engine.py)   │                              │
│              └──────┬─────────────┘                              │
│                     │                                            │
│          ┌──────────┼──────────┐                                 │
│          ↓          ↓          ↓                                 │
│   ┌──────────┐ ┌───────────┐ ┌─────────┐                        │
│   │ Document │ │  Vector   │ │   QA    │                        │
│   │  Loader  │ │   Store   │ │  Chain  │                        │
│   └──────────┘ └───────────┘ └─────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┼────────────────────────────────────────┐
│                         │    Integration Layer                   │
├─────────────────────────┼────────────────────────────────────────┤
│                         ↓                                        │
│   ┌──────────────────────────────────────┐                      │
│   │         LangChain Framework          │                      │
│   ├──────────────────────────────────────┤                      │
│   │  - Document Loaders (PDF/TXT/DOCX)  │                      │
│   │  - Text Splitters                    │                      │
│   │  - Embeddings Interface              │                      │
│   │  - Vector Store Interface            │                      │
│   │  - Retrieval Chains                  │                      │
│   └──────────┬───────────────────┬───────┘                      │
│              │                   │                               │
└──────────────┼───────────────────┼───────────────────────────────┘
               │                   │
┌──────────────┼───────────────────┼───────────────────────────────┐
│              │  Service Layer    │                               │
├──────────────┼───────────────────┼───────────────────────────────┤
│              ↓                   ↓                               │
│   ┌──────────────────┐  ┌──────────────────┐                    │
│   │   ChromaDB       │  │ Sentence Trans.  │                    │
│   │  Vector Store    │  │   Embeddings     │                    │
│   │   (Local DB)     │  │   (HuggingFace)  │                    │
│   └──────────────────┘  └──────────────────┘                    │
│                                                                   │
│   ┌──────────────────────────────────────┐                      │
│   │     Ollama LLM Service               │                      │
│   │     (Windows @ localhost:11434)      │                      │
│   │     - Model: llama2/mistral/etc      │                      │
│   │     - HTTP API                       │                      │
│   └──────────────────────────────────────┘                      │
└───────────────────────────────────────────────────────────────────┘
               │
┌──────────────┼───────────────────────────────────────────────────┐
│              │       Platform Layer                              │
├──────────────┼───────────────────────────────────────────────────┤
│              ↓                                                   │
│   ┌──────────────────────────────────────┐                      │
│   │  WSL Oracle Linux (Application)      │                      │
│   └──────────────────────────────────────┘                      │
│                      ↕                                           │
│   ┌──────────────────────────────────────┐                      │
│   │  Windows (Ollama Service)            │                      │
│   └──────────────────────────────────────┘                      │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Indexing Flow

```
1. User adds documents → data/documents/
                ↓
2. User runs: python -m src.cli index
                ↓
3. RAG Engine:
   - Loads documents (PDF/TXT/DOCX)
   - Splits into chunks (1000 chars, 200 overlap)
   - Generates embeddings (Sentence Transformers)
   - Stores in ChromaDB
                ↓
4. Vector Store Created → data/vector_store/
```

### Query Flow

```
1. User asks question (CLI or Web)
                ↓
2. RAG Engine receives query
                ↓
3. Query Embedding:
   - Convert question to vector
   - Using same embedding model
                ↓
4. Similarity Search:
   - Search vector store
   - Retrieve top 3 relevant chunks
   - Get source documents
                ↓
5. Context Building:
   - Combine retrieved chunks
   - Create prompt with context
                ↓
6. LLM Call:
   - Send to Ollama (Windows)
   - Model generates answer
                ↓
7. Response Assembly:
   - Answer text
   - Source documents
   - Metadata
                ↓
8. Display to User:
   - Formatted answer
   - Source attribution
```

## Component Details

### RAG Engine

**Responsibilities:**
- Document lifecycle management
- Vector store operations
- Query orchestration
- LLM interaction

**Key Classes:**
- `RAGEngine`: Main orchestrator

**Key Methods:**
- `load_documents()`: Multi-format loading
- `split_documents()`: Intelligent chunking
- `create_vector_store()`: Index creation
- `load_vector_store()`: Index loading
- `initialize_qa_chain()`: Chain setup
- `query()`: Question answering

### Document Processing Pipeline

```
Input Document
      ↓
File Type Detection
      ↓
Appropriate Loader
      ├── PDF → PyPDFLoader
      ├── TXT → TextLoader
      └── DOCX → Docx2txtLoader
      ↓
Text Extraction
      ↓
Text Splitter (Recursive)
      ├── Chunk Size: 1000
      └── Overlap: 200
      ↓
Document Chunks
```

### Embedding Pipeline

```
Text Chunk
      ↓
Sentence Transformer Model
(all-MiniLM-L6-v2)
      ↓
384-dimensional Vector
      ↓
ChromaDB Storage
```

### Query Pipeline

```
User Question
      ↓
Embedding Generation
      ↓
Vector Similarity Search (ChromaDB)
      ├── Top K=3
      └── Cosine Similarity
      ↓
Retrieved Documents
      ↓
Prompt Template
      ├── Context: {retrieved_docs}
      └── Question: {user_question}
      ↓
Ollama LLM (Windows)
      ↓
Generated Answer
```

## Configuration Architecture

```
Environment Variables (.env)
           ↓
    config.py (Load & Validate)
           ↓
    ┌──────┴──────┐
    ↓             ↓
RAG Engine    Interfaces
```

**Configuration Hierarchy:**
1. Default values in config.py
2. .env file overrides
3. Command-line arguments (highest priority)

## Interface Architecture

### CLI Interface

```
Click Command Group
      ├── index
      │   ├── Options: --documents-path, --ollama-url, --ollama-model
      │   └── Action: Create vector store
      ├── query
      │   ├── Options: -q, -i, --ollama-url, --ollama-model
      │   └── Action: Answer questions
      └── info
          └── Action: Display system status
```

**Output:**
- Rich console formatting
- Color-coded messages
- Progress indicators
- Source attribution

### Web Interface

```
Streamlit App
      ├── Main Area
      │   ├── Title
      │   ├── Chat History
      │   ├── User Input
      │   └── Responses with Sources
      └── Sidebar
          ├── Configuration Info
          ├── Setup Instructions
          └── About Section
```

**Features:**
- Session state management
- Chat history
- Source document expansion
- Clear chat button

## Network Architecture

```
┌─────────────────────────────────────┐
│         WSL Oracle Linux            │
│                                     │
│  ┌───────────────────────────────┐ │
│  │     RAG One Application       │ │
│  │  - CLI/Web Interface          │ │
│  │  - RAG Engine                 │ │
│  │  - ChromaDB (local)           │ │
│  │  - Sentence Transformers      │ │
│  └───────────┬───────────────────┘ │
│              │                     │
│              │ HTTP                │
│              │ localhost:11434     │
└──────────────┼─────────────────────┘
               │
               ↓ (WSL → Windows)
┌──────────────┼─────────────────────┐
│              │      Windows        │
│  ┌───────────┴───────────────────┐ │
│  │    Ollama Service             │ │
│  │    - HTTP API :11434          │ │
│  │    - Models: llama2, etc      │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Network Communication:**
- Protocol: HTTP
- Port: 11434
- Direction: WSL → Windows
- Method: REST API calls

## Storage Architecture

```
data/
├── documents/              # Input Documents
│   ├── *.pdf              # User PDFs
│   ├── *.txt              # User text files
│   └── *.docx             # User Word docs
│
└── vector_store/           # ChromaDB Storage
    ├── chroma.sqlite3     # SQLite database
    └── [embeddings]       # Vector data
```

## Error Handling Architecture

```
User Action
      ↓
Try Operation
      ├── Success → Display Result
      └── Error
          ├── Catch Exception
          ├── Log Error
          ├── Display User-Friendly Message
          └── Suggest Solution
```

**Error Categories:**
1. Configuration Errors
2. Connection Errors (Ollama)
3. Document Processing Errors
4. Vector Store Errors
5. Query Errors

## Security Architecture

**Security Layers:**
1. **No External APIs**: All processing local
2. **No Secrets in Code**: Environment-based config
3. **Local Data Storage**: No cloud transmission
4. **Configurable Access**: User controls Ollama connection
5. **Input Validation**: Safe document processing

## Scalability Considerations

**Current Design:**
- Single-user desktop application
- Local storage
- Synchronous processing

**Scalability Options:**
- Add batch processing for large document sets
- Implement async query processing
- Add caching layer for repeated queries
- Database optimization for large vector stores
- Distributed vector storage (if needed)

## Technology Decisions

| Decision | Technology | Rationale |
|----------|-----------|-----------|
| RAG Framework | LangChain | Mature, flexible, well-documented |
| Vector Store | ChromaDB | Easy setup, persistent, fast |
| Embeddings | Sentence Transformers | Good quality, runs locally |
| LLM | Ollama | Local, private, free |
| Web UI | Streamlit | Rapid development, good UX |
| CLI | Click + Rich | Professional, user-friendly |

## Performance Characteristics

**Indexing:**
- Speed: ~30-60 seconds for 5-10 documents
- Memory: Moderate (depends on document size)
- Disk: Vector store ~MB per document

**Querying:**
- Speed: 2-5 seconds per query
- Memory: Low (only active context)
- Network: Local HTTP to Ollama

## Deployment Model

```
Development:
- Local WSL environment
- Python virtual environment
- Configuration via .env

Production Options:
- Same as development
- Docker container (future)
- Systemd service (future)
```

## Monitoring & Logging

**Current:**
- Console output (Rich formatting)
- Error messages
- Progress indicators

**Future Enhancements:**
- Log file support
- Metrics collection
- Performance monitoring
- Query analytics

---

This architecture provides a solid, maintainable foundation for document Q&A while maintaining simplicity and local operation.
