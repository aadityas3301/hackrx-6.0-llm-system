#!/usr/bin/env python3
"""
Test script for HackRx 6.0 API
"""

import requests
import json
import time
from typing import Dict, Any

def test_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Test API health endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_main_endpoint(base_url: str = "http://localhost:8000") -> bool:
    """Test the main /hackrx/run endpoint"""
    
    # Test data
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?"
        ]
    }
    
    headers = {
        "Authorization": "Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8",
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Testing main endpoint...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main endpoint test passed!")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"📊 Number of questions: {len(test_data['questions'])}")
            print(f"📝 Number of answers: {len(result.get('answers', []))}")
            print(f"🎯 Confidence scores: {result.get('confidence_scores', [])}")
            
            # Print first answer as example
            if result.get('answers'):
                print(f"\n📋 Sample Answer:")
                print(f"Q: {test_data['questions'][0]}")
                print(f"A: {result['answers'][0]}")
            
            return True
        else:
            print(f"❌ Main endpoint test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint test error: {str(e)}")
        return False

def test_invalid_token(base_url: str = "http://localhost:8000") -> bool:
    """Test with invalid token"""
    test_data = {
        "documents": "https://example.com/test.pdf",
        "questions": ["Test question"]
    }
    
    headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 401:
            print("✅ Invalid token test passed (correctly rejected)")
            return True
        else:
            print(f"❌ Invalid token test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid token test error: {str(e)}")
        return False

def test_missing_token(base_url: str = "http://localhost:8000") -> bool:
    """Test without token"""
    test_data = {
        "documents": "https://example.com/test.pdf",
        "questions": ["Test question"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 401:
            print("✅ Missing token test passed (correctly rejected)")
            return True
        else:
            print(f"❌ Missing token test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Missing token test error: {str(e)}")
        return False

def run_all_tests(base_url: str = "http://localhost:8000"):
    """Run all tests"""
    print("🧪 Starting API Tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", lambda: test_api_health(base_url)),
        ("Main Endpoint", lambda: test_main_endpoint(base_url)),
        ("Invalid Token", lambda: test_invalid_token(base_url)),
        ("Missing Token", lambda: test_missing_token(base_url))
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    import sys
    
    # Allow custom base URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🌐 Testing API at: {base_url}")
    run_all_tests(base_url) 