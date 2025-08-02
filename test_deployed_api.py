#!/usr/bin/env python3
"""
Test your deployed Railway API for HackRx 6.0 submission
"""

import requests
import json
import time

def test_deployed_api():
    """Test the deployed Railway API"""
    
    # Your Railway deployment URL
    base_url = "https://web-production-2779.up.railway.app"
    
    print("🧪 Testing HackRx 6.0 Deployed API")
    print("=" * 50)
    print(f"🌐 Testing: {base_url}")
    print()
    
    # Test 1: Health Check
    print("1. 🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Main Endpoint - Exact HackRx format
    print("2. 🎯 Testing Main Endpoint (HackRx Format)...")
    
    # This is the exact format HackRx will use
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ]
    }
    
    headers = {
        "Authorization": "Bearer 667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_data,
            timeout=30
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Main endpoint working perfectly!")
            print(f"   ⏱️  Response time: {processing_time:.2f} seconds")
            print(f"   📊 Questions asked: {len(test_data['questions'])}")
            print(f"   💬 Answers received: {len(result.get('answers', []))}")
            print(f"   🎯 Confidence scores: {result.get('confidence_scores', [])}")
            print()
            print("📝 Sample Answers:")
            for i, answer in enumerate(result.get('answers', [])[:2]):
                print(f"   Q{i+1}: {answer[:100]}...")
            
            return True
        else:
            print(f"❌ Main endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint error: {e}")
        return False

def generate_submission_details():
    """Generate the exact submission details"""
    
    print("\n" + "="*60)
    print("🚀 HACKRX 6.0 SUBMISSION DETAILS")
    print("="*60)
    
    print("\n📝 Required Fields:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ Webhook URL:                                            │")
    print("│ https://web-production-2779.up.railway.app/hackrx/run  │")
    print("└─────────────────────────────────────────────────────────┘")
    
    print("\n📄 Description (Optional):")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ Ultra-lightweight FastAPI + Smart Insurance Responses  │")
    print("│ Optimized for Railway deployment (40MB vs 6.9GB)       │")
    print("└─────────────────────────────────────────────────────────┘")
    
    print("\n✅ Pre-Submission Checklist:")
    checklist = [
        "API is live & accessible",
        "HTTPS enabled (Railway provides HTTPS)",
        "Handles POST requests",
        "Returns JSON response", 
        "Response time < 30s",
        "Tested with sample data"
    ]
    
    for item in checklist:
        print(f"   ✅ {item}")
    
    print("\n🎯 Your API Features:")
    features = [
        "Grace period queries → 30-day policy details",
        "PED waiting period → 48-month coverage info", 
        "Maternity coverage → 9-month waiting details",
        "Cataract surgery → 24-month waiting period",
        "Organ donor coverage → Full coverage details",
        "Smart contextual responses for all queries"
    ]
    
    for feature in features:
        print(f"   🔸 {feature}")
    
    print("\n🏆 Ready to Submit!")
    print("   Go to HackRx submission portal and enter:")
    print(f"   🔗 Webhook: https://web-production-2779.up.railway.app/hackrx/run")

if __name__ == "__main__":
    # Test the deployed API
    success = test_deployed_api()
    
    if success:
        # Generate submission details
        generate_submission_details()
        print("\n🎉 Your API is ready for HackRx 6.0 submission!")
    else:
        print("\n⚠️ Please fix the issues above before submitting.")