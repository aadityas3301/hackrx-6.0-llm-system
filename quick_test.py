#!/usr/bin/env python3
"""
Quick test script for HackRx 6.0 API
"""

import requests
import json
import sys

def test_api(base_url="http://127.0.0.1:8001"):
    """Test the API endpoints"""
    
    print(f"🧪 Testing API at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Main endpoint
    print("\n2. Testing main endpoint...")
    
    headers = {
        "Authorization": "Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8",
        "Content-Type": "application/json"
    }
    
    data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/hackrx/run", headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main endpoint test passed!")
            print(f"⏱️  Processing time: {result.get('processing_time', 0):.2f} seconds")
            print(f"📝 Number of answers: {len(result.get('answers', []))}")
            print(f"🎯 Confidence scores: {result.get('confidence_scores', [])}")
            
            # Show first answer
            if result.get('answers'):
                print(f"\n📋 Sample Answer:")
                print(f"Q: {data['questions'][0]}")
                print(f"A: {result['answers'][0]}")
            
            return True
        else:
            print(f"❌ Main endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint error: {e}")
        return False

if __name__ == "__main__":
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
    
    success = test_api(base_url)
    
    if success:
        print("\n🎉 All tests passed! Your API is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Create GitHub repository")
        print("2. Push your code to GitHub")
        print("3. Deploy to Vercel")
        print("4. Submit to HackRx platform")
        print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        sys.exit(1)