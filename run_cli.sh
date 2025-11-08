#!/bin/bash
# Convenience script to run RAG One CLI

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Run the CLI with provided arguments
python -m src.cli "$@"
