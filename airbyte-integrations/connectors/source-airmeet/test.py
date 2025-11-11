#!/usr/bin/env python
"""
Test script for Airmeet connector
"""
import json
import subprocess
import sys
import requests


def test_auth_directly():
    """Test authentication directly with Airmeet API"""
    print("\n🔐 Testing Airmeet Authentication Directly...")
    
    headers = {
        "Content-Type": "application/json",
        "x-airmeet-access-key": "ebd842ce-9e5c-4941-89f4-a681e1eb114a#in",
        "x-airmeet-secret-key": "9c4bdac4-b658-4b04-b20d-3d0394fdda1e"
    }
    
    response = requests.post(
        "https://api-gateway.airmeet.com/prod/auth",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Auth successful! Token: {data.get('token')[:50]}...")
        print(f"   Community ID: {data.get('communityId')}")
        return data.get('token')
    else:
        print(f"❌ Auth failed: {response.status_code}")
        print(response.text)
        return None


def test_airmeets_api(token):
    """Test fetching airmeets with token"""
    print("\n📋 Testing Airmeets API...")
    
    headers = {
        "Content-Type": "application/json",
        "x-airmeet-access-token": token
    }
    
    response = requests.get(
        "https://api-gateway.airmeet.com/prod/airmeets",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API call successful! Found {len(data.get('data', []))} airmeets")
        return True
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(response.text)
        return False


def run_connector_test(cmd):
    """Run connector command"""
    print(f"\n🚀 Running: {' '.join(cmd)}")
    print("-" * 50)
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        try:
            output = json.loads(result.stdout)
            print(json.dumps(output, indent=2))
        except:
            print(result.stdout)
    
    if result.stderr:
        print(f"Stderr: {result.stderr}")
    
    return result.returncode == 0


def main():
    # Test direct API calls first
    token = test_auth_directly()
    if token:
        test_airmeets_api(token)
    
    # Test connector
    print("\n" + "="*60)
    print("Testing Connector")
    print("="*60)
    
    base_cmd = ["poetry", "run", "python", "main.py"]
    
    # Test spec
    if not run_connector_test(base_cmd + ["spec"]):
        print("❌ Spec test failed")
        return 1
    
    # Test check
    if not run_connector_test(base_cmd + ["check", "--config", "secrets/config.json"]):
        print("❌ Connection check failed")
        return 1
    
    # Test discover
    if not run_connector_test(base_cmd + ["discover", "--config", "secrets/config.json"]):
        print("❌ Discover test failed")
        return 1
    
    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())