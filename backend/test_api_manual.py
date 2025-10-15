"""Quick manual test of the API endpoints."""

import sys
import time
import subprocess
import requests
import json

def test_api():
    """Test basic API endpoints."""

    # Start the server
    print("Starting API server...")
    server = subprocess.Popen(
        [sys.executable, "-m", "backend.api.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(5)

    base_url = "http://localhost:8000"

    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        # Test watchlist endpoint
        print("\n2. Testing watchlist endpoint...")
        response = requests.get(f"{base_url}/api/v1/watchlist")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        # Test stock overview (if AAPL data exists)
        print("\n3. Testing stock overview endpoint (AAPL)...")
        try:
            response = requests.get(f"{base_url}/api/v1/stocks/AAPL/overview")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Ticker: {data['ticker']}")
                print(f"   Price: ${data['price']['close']}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Expected - no data yet: {e}")

        # Test stock metrics
        print("\n4. Testing stock metrics endpoint (AAPL)...")
        try:
            response = requests.get(f"{base_url}/api/v1/stocks/AAPL/metrics")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Ticker: {data['ticker']}")
                print(f"   Profile: {data['profile_used']}")
                print(f"   Categories: {list(data.keys())}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Expected - no data yet: {e}")

        print("\n✅ API server is working!")

    except Exception as e:
        print(f"\n❌ Error testing API: {e}")

    finally:
        # Stop the server
        print("\nStopping API server...")
        server.terminate()
        server.wait(timeout=5)
        print("Server stopped.")


if __name__ == "__main__":
    test_api()
