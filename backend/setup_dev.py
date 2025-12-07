"""Quick setup script for development environment."""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if not env_example.exists():
        print("✗ .env.example not found")
        return
    
    # Copy example to .env
    env_file.write_text(env_example.read_text())
    print("✓ Created .env file from .env.example")
    print("⚠ Please edit .env and add your API keys")


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 11):
        print(f"✗ Python 3.11+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_uv_installed():
    """Check if uv is installed."""
    try:
        import subprocess
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ uv {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ uv not installed. Install with: pip install uv")
    return False


def main():
    """Run setup checks."""
    print("=== Backend Setup Check ===\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check uv
    uv_ok = check_uv_installed()
    
    # Create .env file
    create_env_file()
    
    print("\n=== Next Steps ===")
    print("1. Edit .env and add your API keys (OPENAI_API_KEY, QDRANT_URL, etc.)")
    print("2. Install dependencies: uv pip install -r requirements.txt")
    print("3. Start Docker services: docker-compose up -d postgres qdrant redis")
    print("4. Run migrations: alembic upgrade head")
    print("5. Index sample content: python scripts/ingest_to_qdrant.py --docs ../docs --collection physical_ai_humanoid_robotics_course")
    print("6. Start server: uvicorn app.main:app --reload")
    print("\nAPI will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
