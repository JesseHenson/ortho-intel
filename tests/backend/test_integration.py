#!/usr/bin/env python3
"""
Integration test script to validate the complete system
"""

import requests
import time
import os
from tests.backend.test_dataset import get_test_request, TestRunner

def test_api_health():
    """Test if API is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True, response.json()
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False, None

def test_full_workflow():
    """Test the complete analysis workflow"""
    print("🧪 Testing full competitive intelligence workflow...")
    
    # Check API health first
    api_healthy, health_info = test_api_health()
    if not api_healthy:
        print("❌ Cannot run workflow test - API not available")
        return False
    
    print("📊 Health info:", health_info)
    
    # Get test request
    test_req = get_test_request()
    print(f"🎯 Testing with: {test_req.competitors}")
    
    # Run synchronous analysis
    try:
        print("⏳ Starting analysis (this may take 2-5 minutes)...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/analyze-gaps-sync",
            json=test_req.model_dump(),
            timeout=300  # 5 minutes
        )
        
        if response.status_code != 200:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        result = response.json()
        end_time = time.time()
        
        print(f"✅ Analysis completed in {end_time - start_time:.1f} seconds")
        
        # Validate results
        print("🔍 Validating results...")
        validation_results = TestRunner.run_basic_validation(result, test_req)
        all_passed = TestRunner.print_validation_results(validation_results)
        
        if all_passed:
            print("🎉 All tests passed!")
            print(f"📈 Found {len(result.get('clinical_gaps', []))} gaps and {len(result.get('market_opportunities', []))} opportunities")
            return True
        else:
            print("⚠️ Some validation tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Analysis failed with exception: {str(e)}")
        return False

def check_environment():
    """Check if environment is properly configured"""
    print("🔧 Checking environment configuration...")
    
    required_vars = ["TAVILY_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure to set these in your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

if __name__ == "__main__":
    print("🧪 ORTHOPEDIC COMPETITIVE INTELLIGENCE - Integration Tests")
    print("=" * 60)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ Environment check failed. Please fix configuration and try again.")
        exit(1)
    
    # Test full workflow
    workflow_ok = test_full_workflow()
    
    print("\n" + "=" * 60)
    if workflow_ok:
        print("🎉 ALL TESTS PASSED - System is ready for use!")
        print("\n📋 Next steps:")
        print("1. Start Streamlit frontend: streamlit run streamlit_frontend.py") 
        print("2. Access the app at: http://localhost:8501")
    else:
        print("❌ TESTS FAILED - Please check the issues above")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure FastAPI server is running: python fastapi_server.py")
        print("2. Check your API keys in .env file")
        print("3. Verify internet connection for Tavily API")