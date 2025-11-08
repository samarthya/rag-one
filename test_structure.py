#!/usr/bin/env python3
"""Basic structure tests for RAG One (no external dependencies needed)."""

import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported syntactically."""
    print("Testing module imports...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test syntax by compiling
        import py_compile
        
        modules = [
            'src/__init__.py',
            'src/config.py',
            'src/rag_engine.py',
            'src/cli.py',
            'src/web_ui.py',
        ]
        
        all_ok = True
        for module in modules:
            try:
                py_compile.compile(module, doraise=True)
                print(f"  ✅ {module} - syntax OK")
            except py_compile.PyCompileError as e:
                print(f"  ❌ {module} - syntax error: {e}")
                all_ok = False
        
        return all_ok
    
    except Exception as e:
        print(f"  ❌ Error during import test: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'README_DETAILED.md',
        'QUICKSTART.md',
        'EXAMPLES.md',
        'setup.sh',
        'run_cli.sh',
        'run_web.sh',
        'verify_setup.py',
        'src/__init__.py',
        'src/config.py',
        'src/rag_engine.py',
        'src/cli.py',
        'src/web_ui.py',
        'data/documents/sample_doc1.txt',
        'data/documents/sample_doc2.txt',
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - missing")
            all_exist = False
    
    return all_exist


def test_script_permissions():
    """Test that shell scripts are executable."""
    print("\nTesting script permissions...")
    
    scripts = [
        'setup.sh',
        'run_cli.sh',
        'run_web.sh',
    ]
    
    all_executable = True
    for script in scripts:
        path = Path(script)
        if path.exists():
            import os
            if os.access(path, os.X_OK):
                print(f"  ✅ {script} - executable")
            else:
                print(f"  ⚠️  {script} - not executable (may need chmod +x)")
                all_executable = False
        else:
            print(f"  ❌ {script} - missing")
            all_executable = False
    
    return all_executable


def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'src',
        'data',
        'data/documents',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ - missing or not a directory")
            all_exist = False
    
    return all_exist


def test_requirements():
    """Test that requirements.txt has expected content."""
    print("\nTesting requirements.txt...")
    
    required_packages = [
        'langchain',
        'ollama',
        'chromadb',
        'streamlit',
        'click',
        'rich',
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        all_present = True
        for package in required_packages:
            if package in content:
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package} - not in requirements.txt")
                all_present = False
        
        return all_present
    
    except Exception as e:
        print(f"  ❌ Error reading requirements.txt: {e}")
        return False


def test_env_example():
    """Test that .env.example has required configuration."""
    print("\nTesting .env.example...")
    
    required_vars = [
        'OLLAMA_BASE_URL',
        'OLLAMA_MODEL',
        'VECTOR_STORE_TYPE',
        'VECTOR_STORE_PATH',
        'DOCUMENTS_PATH',
    ]
    
    try:
        with open('.env.example', 'r') as f:
            content = f.read()
        
        all_present = True
        for var in required_vars:
            if var in content:
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var} - not in .env.example")
                all_present = False
        
        return all_present
    
    except Exception as e:
        print(f"  ❌ Error reading .env.example: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("RAG One Structure Tests")
    print("=" * 60)
    
    tests = [
        test_directory_structure,
        test_file_structure,
        test_script_permissions,
        test_requirements,
        test_env_example,
        test_imports,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All structure tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run verification: python verify_setup.py")
        print("3. Start using: python -m src.cli index")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
