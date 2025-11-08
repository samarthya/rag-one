# Contributing to RAG One

Thank you for your interest in contributing to RAG One! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rag-one.git
   cd rag-one
   ```
3. Set up development environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

## Testing

Before submitting:

1. Run structure tests:
   ```bash
   python test_structure.py
   ```

2. Test your changes manually:
   ```bash
   # Test CLI
   python -m src.cli index
   python -m src.cli query -i
   
   # Test Web UI
   streamlit run src/web_ui.py
   ```

3. Verify setup:
   ```bash
   python verify_setup.py
   ```

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Test thoroughly
4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Areas for Contribution

- Additional document format support
- Performance improvements
- UI enhancements
- Documentation improvements
- Bug fixes
- Test coverage
- Integration with other LLMs
- Docker support

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Questions about the code
- Documentation improvements

Thank you for contributing!
