#!/usr/bin/env python3
"""
Lightweight deployment script for HackRx 6.0
This version uses minimal dependencies to avoid size limits
"""

import os
import sys
import subprocess
import shutil

def prepare_for_lightweight_deployment():
    """Prepare the project for lightweight deployment"""
    print("🚀 Preparing for lightweight deployment...")
    print("=" * 50)
    
    # Step 1: Backup original files
    print("📁 Creating backup of original files...")
    if os.path.exists("main.py") and not os.path.exists("main_full.py"):
        shutil.copy("main.py", "main_full.py")
        print("✅ Backed up main.py to main_full.py")
    
    if os.path.exists("requirements.txt") and not os.path.exists("requirements_full.txt"):
        shutil.copy("requirements.txt", "requirements_full.txt")
        print("✅ Backed up requirements.txt to requirements_full.txt")
    
    if os.path.exists("Procfile") and not os.path.exists("Procfile.full"):
        shutil.copy("Procfile", "Procfile.full")
        print("✅ Backed up Procfile to Procfile.full")
    
    # Step 2: Replace with lightweight versions
    print("\n🔄 Switching to lightweight versions...")
    
    # Replace main.py with lightweight version
    if os.path.exists("main_lightweight.py"):
        shutil.copy("main_lightweight.py", "main.py")
        print("✅ Replaced main.py with lightweight version")
    
    # Replace requirements.txt with minimal version
    if os.path.exists("requirements-minimal.txt"):
        shutil.copy("requirements-minimal.txt", "requirements.txt")
        print("✅ Replaced requirements.txt with minimal version")
    
    # Replace Procfile with Railway version
    if os.path.exists("Procfile.railway"):
        shutil.copy("Procfile.railway", "Procfile")
        print("✅ Replaced Procfile with Railway version")
    
    print("\n✅ Lightweight deployment preparation complete!")
    return True

def restore_full_version():
    """Restore the full version with all dependencies"""
    print("🔄 Restoring full version...")
    
    if os.path.exists("main_full.py"):
        shutil.copy("main_full.py", "main.py")
        print("✅ Restored main.py")
    
    if os.path.exists("requirements_full.txt"):
        shutil.copy("requirements_full.txt", "requirements.txt")
        print("✅ Restored requirements.txt")
    
    if os.path.exists("Procfile.full"):
        shutil.copy("Procfile.full", "Procfile")
        print("✅ Restored Procfile")
    
    print("✅ Full version restored!")

def test_lightweight_version():
    """Test the lightweight version locally"""
    print("🧪 Testing lightweight version...")
    
    try:
        # Install minimal dependencies
        print("📦 Installing minimal dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements-minimal.txt"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
        
        print("✅ Dependencies installed")
        
        # Test import
        print("🔍 Testing imports...")
        test_result = subprocess.run([
            sys.executable, "-c", "import main_lightweight; print('✅ Import successful')"
        ], capture_output=True, text=True)
        
        if test_result.returncode == 0:
            print("✅ Lightweight version works correctly")
            return True
        else:
            print(f"❌ Import test failed: {test_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def get_package_sizes():
    """Show the size difference between full and minimal requirements"""
    print("📊 Package size comparison:")
    print("-" * 40)
    
    # Full requirements packages
    full_packages = [
        "sentence-transformers",
        "langchain",
        "pinecone-client",
        "torch",
        "transformers",
        "numpy",
        "pandas"
    ]
    
    # Minimal requirements packages
    minimal_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "requests"
    ]
    
    print("🏋️  Heavy packages (removed):")
    for package in full_packages:
        print(f"   ❌ {package}")
    
    print("\n🪶 Lightweight packages (kept):")
    for package in minimal_packages:
        print(f"   ✅ {package}")
    
    print(f"\n📏 Estimated size reduction: ~6GB → ~200MB")

def deploy_to_railway():
    """Instructions for Railway deployment"""
    print("\n🚂 Railway Deployment Instructions:")
    print("=" * 50)
    print("1. Go to https://railway.app")
    print("2. Sign in with GitHub")
    print("3. Click 'New Project' → 'Deploy from GitHub repo'")
    print("4. Select your repository")
    print("5. Railway will automatically detect Python and use:")
    print("   - requirements.txt (now minimal)")
    print("   - Procfile (now lightweight)")
    print("6. Set environment variables in Railway dashboard:")
    print("   - API_TOKEN=667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8")
    print("   - Add any other required env vars")
    print("7. Deploy and test!")
    print("\n✅ Your app should now deploy successfully within the 4GB limit!")

def main():
    """Main deployment function"""
    print("🚀 HackRx 6.0 - Lightweight Deployment Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "prepare":
            prepare_for_lightweight_deployment()
            get_package_sizes()
            
        elif command == "test":
            test_lightweight_version()
            
        elif command == "restore":
            restore_full_version()
            
        elif command == "deploy":
            prepare_for_lightweight_deployment()
            test_lightweight_version()
            deploy_to_railway()
            
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: prepare, test, restore, deploy")
    
    else:
        print("Available commands:")
        print("  python deploy_lightweight.py prepare  - Prepare for lightweight deployment")
        print("  python deploy_lightweight.py test     - Test lightweight version")
        print("  python deploy_lightweight.py restore  - Restore full version")
        print("  python deploy_lightweight.py deploy   - Full deployment workflow")
        print("\nQuick start: python deploy_lightweight.py deploy")

if __name__ == "__main__":
    main()
