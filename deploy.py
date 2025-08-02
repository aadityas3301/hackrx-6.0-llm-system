#!/usr/bin/env python3
"""
Deployment script for HackRx 6.0
"""

import os
import subprocess
import sys
import json
from typing import Dict, Any

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found")
        return False
    
    print("✅ main.py found")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration (Optional - will fall back to in-memory if not provided)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter

# API Configuration
API_TOKEN=667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CHUNKS=100

# Vector Search
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update the API keys in .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_local():
    """Test the application locally"""
    print("🧪 Testing application locally...")
    
    try:
        # Start the server in background
        process = subprocess.Popen([sys.executable, "main.py"])
        
        # Wait a bit for server to start
        import time
        time.sleep(3)
        
        # Test the API
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Local test passed")
                process.terminate()
                return True
            else:
                print(f"❌ Local test failed: {response.status_code}")
                process.terminate()
                return False
        except Exception as e:
            print(f"❌ Local test error: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Failed to start local server: {e}")
        return False

def deploy_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    try:
        subprocess.run(["heroku", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    
    if not app_name:
        try:
            result = subprocess.run(["heroku", "create"], check=True, capture_output=True, text=True)
            app_name = result.stdout.strip().split("/")[-1]
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Heroku app: {e}")
            return False
    else:
        try:
            subprocess.run(["heroku", "create", app_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Heroku app: {e}")
            return False
    
    print(f"✅ Heroku app created: {app_name}")
    
    # Set environment variables
    openai_key = input("Enter your OpenAI API key: ").strip()
    pinecone_key = input("Enter your Pinecone API key (optional): ").strip()
    
    try:
        subprocess.run(["heroku", "config:set", f"OPENAI_API_KEY={openai_key}"], check=True)
        if pinecone_key:
            subprocess.run(["heroku", "config:set", f"PINECONE_API_KEY={pinecone_key}"], check=True)
        print("✅ Environment variables set")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set environment variables: {e}")
        return False
    
    # Deploy
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Deploy to Heroku"], check=True)
        subprocess.run(["git", "push", "heroku", "main"], check=True)
        print("✅ Deployed to Heroku successfully")
        
        # Get the URL
        result = subprocess.run(["heroku", "info", "-s"], check=True, capture_output=True, text=True)
        for line in result.stdout.split("\n"):
            if line.startswith("web_url="):
                url = line.split("=")[1]
                print(f"🌐 Your API is available at: {url}")
                break
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to deploy: {e}")
        return False

def deploy_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found. Please install it first:")
        print("   npm install -g @railway/cli")
        return False
    
    print("📋 Railway deployment steps:")
    print("1. Run: railway login")
    print("2. Run: railway init")
    print("3. Set environment variables in Railway dashboard")
    print("4. Run: railway up")
    
    return True

def deploy_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Vercel CLI not found. Please install it first:")
        print("   npm install -g vercel")
        return False
    
    print("📋 Vercel deployment steps:")
    print("1. Run: vercel login")
    print("2. Set environment variables:")
    print("   - OPENAI_API_KEY")
    print("   - PINECONE_API_KEY (optional)")
    print("3. Run: vercel --prod")
    
    return True

def main():
    """Main deployment function"""
    print("🚀 HackRx 6.0 Deployment Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Create .env file
    create_env_file()
    
    # Show menu
    print("\n📋 Deployment Options:")
    print("1. Test locally")
    print("2. Deploy to Heroku")
    print("3. Deploy to Railway")
    print("4. Deploy to Vercel")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        test_local()
    elif choice == "2":
        deploy_heroku()
    elif choice == "3":
        deploy_railway()
    elif choice == "4":
        deploy_vercel()
    elif choice == "5":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 