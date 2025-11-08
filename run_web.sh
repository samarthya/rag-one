#!/bin/bash
# Convenience script to run RAG One Web UI

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Run Streamlit
streamlit run src/web_ui.py
