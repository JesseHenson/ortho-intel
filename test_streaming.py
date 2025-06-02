#!/usr/bin/env python3
"""
Simple streaming test client to debug SSE functionality
"""

import requests
import json
import time
from datetime import datetime

def test_basic_endpoints():
    """Test basic API endpoints first"""
    base_url = "http://localhost:8000"
    
    print(f"🔍 Testing basic endpoints at {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    return True

def test_streaming_endpoint(analysis_id="test-streaming-123"):
    """Test streaming endpoint with event source"""
    url = f"http://localhost:8000/stream/{analysis_id}"
    
    print(f"\n🔄 Testing streaming endpoint: {url}")
    
    try:
        response = requests.get(
            url,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ Streaming failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            return False
        
        print("📡 Listening for streaming events...")
        
        event_count = 0
        start_time = time.time()
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(f"📨 [{time.time() - start_time:.1f}s] {line}")
                event_count += 1
                
                # Parse event data
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        print(f"   📋 Parsed: {data}")
                    except json.JSONDecodeError as e:
                        print(f"   ⚠️  JSON parse error: {e}")
                
                # Stop after a few events or timeout
                if event_count >= 5 or (time.time() - start_time) > 10:
                    print(f"🛑 Stopping after {event_count} events")
                    break
        
        print(f"✅ Streaming test completed: {event_count} events received")
        return True
        
    except requests.exceptions.Timeout:
        print("⏰ Streaming test timed out")
        return False
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

def test_trigger_analysis():
    """Test triggering an analysis"""
    url = "http://localhost:8000/stream/trigger/test-analysis-456"
    
    payload = {
        "competitors": ["Stryker", "Medtronic"],
        "focus_area": "Spine Fusion"
    }
    
    print(f"\n🚀 Triggering analysis: {url}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis triggered successfully")
            print(f"   Analysis ID: {result.get('analysis_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return result.get('analysis_id')
        else:
            print(f"❌ Analysis trigger failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis trigger failed: {e}")
        return None

def test_streaming_with_real_analysis():
    """Test streaming with a real triggered analysis"""
    print("\n🎯 Testing full streaming workflow...")
    
    # First trigger an analysis
    analysis_id = test_trigger_analysis()
    if not analysis_id:
        print("❌ Could not trigger analysis, skipping streaming test")
        return False
    
    # Wait a moment
    time.sleep(1)
    
    # Now test streaming for that analysis
    return test_streaming_endpoint(analysis_id)

if __name__ == "__main__":
    print("🧪 Streaming Functionality Test Suite")
    print("=" * 50)
    
    # Test basic endpoints first
    if not test_basic_endpoints():
        print("❌ Basic endpoints failed, stopping tests")
        exit(1)
    
    # Test simple streaming
    print("\n" + "=" * 50)
    test_streaming_endpoint()
    
    # Test triggered analysis streaming
    print("\n" + "=" * 50)
    test_streaming_with_real_analysis()
    
    print("\n✅ All tests completed!") 