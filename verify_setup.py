#!/usr/bin/env python3
"""Verification script to check RAG One setup."""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    required = [
        'langchain',
        'streamlit',
        'click',
        'rich',
        'chromadb',
        'sentence_transformers',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0


def check_directories():
    """Check if required directories exist."""
    dirs = [
        'src',
        'data',
        'data/documents',
    ]
    
    all_exist = True
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")
            all_exist = False
    
    return all_exist


def check_files():
    """Check if required files exist."""
    files = [
        'requirements.txt',
        '.env.example',
        'src/__init__.py',
        'src/config.py',
        'src/rag_engine.py',
        'src/cli.py',
        'src/web_ui.py',
    ]
    
    all_exist = True
    for file_name in files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name}")
            all_exist = False
    
    return all_exist


def check_ollama_connection():
    """Check if Ollama is accessible."""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        import urllib.request
        import urllib.error
        
        try:
            with urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=5) as response:
                if response.status == 200:
                    print(f"✅ Ollama accessible at {ollama_url}")
                    return True
        except urllib.error.URLError:
            print(f"❌ Cannot connect to Ollama at {ollama_url}")
            print(f"   Make sure Ollama is running on Windows")
            return False
    except ImportError:
        print(f"⚠️  Cannot test Ollama connection (dependencies not installed)")
        return None


def main():
    """Run all checks."""
    print("=" * 60)
    print("RAG One Setup Verification")
    print("=" * 60)
    
    print("\n📋 Python Version:")
    python_ok = check_python_version()
    
    print("\n📦 Dependencies:")
    deps_ok = check_dependencies()
    
    print("\n📁 Directories:")
    dirs_ok = check_directories()
    
    print("\n📄 Files:")
    files_ok = check_files()
    
    print("\n🔗 Ollama Connection:")
    ollama_ok = check_ollama_connection()
    
    print("\n" + "=" * 60)
    
    if not deps_ok:
        print("\n⚠️  Dependencies missing. Run:")
        print("   pip install -r requirements.txt")
    
    if not dirs_ok or not files_ok:
        print("\n⚠️  Some files or directories are missing.")
        print("   Make sure you're in the rag-one directory.")
    
    if ollama_ok is False:
        print("\n⚠️  Ollama not accessible. Make sure:")
        print("   1. Ollama is installed and running on Windows")
        print("   2. You can reach Windows from WSL")
        print("   3. Check .env for correct OLLAMA_BASE_URL")
    
    if python_ok and deps_ok and dirs_ok and files_ok and ollama_ok:
        print("\n🎉 All checks passed! You're ready to use RAG One.")
        print("\nNext steps:")
        print("1. Add documents to data/documents/")
        print("2. Run: python -m src.cli index")
        print("3. Run: python -m src.cli query -i")
    elif python_ok and deps_ok and dirs_ok and files_ok:
        print("\n✅ Core setup complete!")
        print("⚠️  Ollama connection needs attention.")
        print("\nYou can still proceed if you fix Ollama connectivity.")
    else:
        print("\n❌ Setup incomplete. Please address the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
