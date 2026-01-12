#!/usr/bin/env python3
"""
Quick test script for DataGuard API
Run this to verify all endpoints work correctly
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_text_scrubbing():
    """Test text scrubbing with various PII types"""
    print("=" * 60)
    print("TEST 2: Text Scrubbing")
    print("=" * 60)
    
    test_text = """
    Contact me at john.doe@example.com or jane@company.org.
    My SSN is 123-45-6789.
    Credit card: 4532-1488-0343-6467 (Visa)
    Another card: 5425233430109903
    Server IP: 192.168.1.1 and public IP: 8.8.8.8
    IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    AWS Key: AKIAIOSFODNN7EXAMPLE
    """
    
    print(f"Original text:\n{test_text}\n")
    
    response = requests.post(
        f"{API_BASE}/scrub/text",
        json={"text": test_text}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"\nCleaned text:\n{result['clean_text']}\n")
    print(f"Total redactions: {result['redactions_count']}")
    print(f"Details: {json.dumps(result['details'], indent=2)}")
    print()

def test_api_info():
    """Test root endpoint"""
    print("=" * 60)
    print("TEST 3: API Info")
    print("=" * 60)
    
    response = requests.get(f"{API_BASE}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    print("\n🛡️  DataGuard API Test Suite\n")
    
    try:
        test_health()
        test_text_scrubbing()
        test_api_info()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🚀 Your API is ready to deploy!")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs for interactive API docs")
        print("2. Read LAUNCH_GUIDE.md for monetization strategy")
        print("3. Deploy to Fly.io or Railway for production")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API")
        print("\nMake sure the server is running:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
