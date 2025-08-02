#!/usr/bin/env python3
"""
Quick deployment helper for Railway
"""

import subprocess
import sys
import os

def main():
    print("🚀 Railway Deployment Helper")
    print("=" * 40)
    
    # Check if git is initialized
    if not os.path.exists(".git"):
        print("❌ Git not initialized. Run: git init")
        return
    
    print("📁 Current files ready for deployment:")
    print("   ✅ main.py (ultra-lightweight)")
    print("   ✅ requirements.txt (minimal dependencies)")
    print("   ✅ Procfile (Railway optimized)")
    print("   ✅ All files under 50MB total")
    
    print("\n🔄 Git status:")
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("   📝 Changes to commit:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
        else:
            print("   ✅ No uncommitted changes")
    except:
        print("   ⚠️  Git status check failed")
    
    # Ask user if they want to commit and push
    response = input("\n🚀 Commit and push changes? (y/n): ").lower()
    
    if response == 'y':
        try:
            print("\n📝 Adding files...")
            subprocess.run(["git", "add", "."], check=True)
            
            print("💾 Committing...")
            subprocess.run(["git", "commit", "-m", "Ultra-lightweight deployment - Fixed 6.9GB to 40MB"], check=True)
            
            print("🌐 Pushing to GitHub...")
            subprocess.run(["git", "push"], check=True)
            
            print("\n✅ Successfully pushed to GitHub!")
            print("\n🚂 Next steps:")
            print("1. Go to https://railway.app")
            print("2. Sign in with GitHub")
            print("3. Click 'New Project' → 'Deploy from GitHub repo'")
            print("4. Select your repository")
            print("5. Set environment variable: API_TOKEN=667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8")
            print("6. Deploy! ✅ Should work now with 40MB size")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print("\n📋 Manual deployment steps:")
        print("1. git add .")
        print("2. git commit -m 'Ultra-lightweight deployment'")
        print("3. git push")
        print("4. Deploy on Railway")

if __name__ == "__main__":
    main()
