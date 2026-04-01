"""Quick API Test Script
Run this to verify the backend is working correctly"""

import requests
import json

def test_backend():
    print("=" * 60)
    print("🧪 Testing MindViz Backend API")
    print("=" * 60)
    print()
    
    # Test 1: Check if server is running
    print("TEST 1: Server Health Check")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"   FastAPI docs accessible at http://localhost:8000/docs")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure you started the backend: cd backend && python server.py")
        return
    
    print()
    
    # Test 2: Test analysis endpoint
    print("TEST 2: Analysis Endpoint")
    test_input = "I'm feeling very stressed and anxious about my exams. I can't focus."
    print(f"Input: '{test_input}'")
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "user_input": test_input,
                "username": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis successful!")
            print()
            print("📊 METRICS:")
            metrics = result.get('metrics', {})
            print(f"   Anxiety: {metrics.get('anxiety', 'N/A')} (0=calm, 1=anxious)")
            print(f"   Mood: {metrics.get('mood', 'N/A')} (0=low, 1=high)")
            print(f"   Stress: {metrics.get('stress', 'N/A')} (0=relaxed, 1=stressed)")
            print()
            
            print("💊 RECOMMENDATIONS:")
            recommendations = result.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec.get('name', 'Unknown')}")
                    print(f"      Duration: {rec.get('duration', 'N/A')} minutes")
                    print(f"      Relevance Score: {rec.get('relevance_score', 'N/A')}")
                    print()
            else:
                print("   ⚠️ No recommendations received!")
            
            print("🌿 VISUALIZATION:")
            viz = result.get('visualization', {})
            print(f"   Overall Wellbeing: {viz.get('wellbeing', 'N/A')}")
            print(f"   Sky Color (RGB): {viz.get('sky_color', 'N/A')}")
            print(f"   Flower Health: {viz.get('flower_health', 'N/A')}")
            print(f"   Rain Intensity: {viz.get('rain_intensity', 'N/A')}")
            print(f"   Cloud Count: {viz.get('cloud_count', 'N/A')}")
            print()
            
            # Save full response for inspection
            with open('test_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print("📄 Full response saved to: test_response.json")
            
        else:
            print(f"❌ Analysis failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Analysis request failed: {e}")
    
    print()
    print("=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_backend()
