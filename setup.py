#!/usr/bin/env python3
"""
Setup script for the AI-Powered Insider Trading Detector.
"""

import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories."""
    dirs = ["models", "logs", "data", "frontend"]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please update .env with your actual API keys")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed")


def main():
    """Main setup function."""
    print("🚀 Setting up AI-Powered Insider Trading Detector")
    print("=" * 50)
    
    check_python_version()
    create_directories()
    create_env_file()
    
    install_deps = input("\n📦 Install Python dependencies? (y/n): ").lower().strip()
    if install_deps in ['y', 'yes']:
        install_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update .env with your Supabase and API keys")
    print("2. Run the Supabase schema: docs/supabase_schema.sql")
    print("3. Test the pipeline: python main.py pipeline")
    print("4. Start the API: python main.py api")
    print("\n📚 See README.md for detailed instructions")


if __name__ == "__main__":
    main()