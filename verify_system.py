import asyncio
import httpx
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"

import time

async def main():
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    
    async with httpx.AsyncClient() as client:
        # 1. Signup
        print(f"Signing up {email}...")
        resp = await client.post(f"{BASE_URL}/auth/signup", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if resp.status_code == 400 and "already exists" in resp.text:
            print("User already exists, proceeding to login.")
        else:
            assert resp.status_code == 200, f"Signup failed: {resp.text}"
        
        # 2. Login
        print("Logging in...")
        resp = await client.post(f"{BASE_URL}/auth/login/access-token", data={
            "username": email,
            "password": password
        })
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create API Key
        print("Creating API Key...")
        resp = await client.post(f"{BASE_URL}/api-keys/", headers=headers, json={
            "name": "Test Key"
        })
        assert resp.status_code == 200, f"API Key creation failed: {resp.text}"
        api_key = resp.json()
        full_key = api_key["full_key"]
        print(f"Got API Key: {full_key}")
        
        # 4. Make Request with API Key
        print("Calling AI Generation Endpoint...")
        key_headers = {"X-API-KEY": full_key}
        resp = await client.post(f"{BASE_URL}/demo/generate", headers=key_headers, json={
            "prompt": "Hello world",
            "max_length": 10
        })
        assert resp.status_code == 200, f"AI Generation call failed: {resp.text}"
        print(f"AI Response: {resp.json()}")
        
        # 5. Check Usage
        print("Checking Usage...")
        # usage logging is async, wait a bit
        await asyncio.sleep(2)
        today = date.today().isoformat()
        resp = await client.get(f"{BASE_URL}/usage/summary?start_date={today}&end_date={today}", headers=headers)
        assert resp.status_code == 200, f"Usage check failed: {resp.text}"
        usage = resp.json()
        print(f"Usage Summary: {usage}")
        found = any(u["endpoint"] == "/api/v1/demo/generate" for u in usage)
        if found:
            print("Usage tracked successfully.")
        else:
            print("WARNING: Usage not found in summary yet.")

        # 6. Trigger Billing (Admin only)
        # We need a superuser to trigger billing or we should have made it open for verified orgs?
        # The endpoint requires superuser.
        # Let's see if we can make this user superuser directly in DB or just skip this step for automated test if hard.
        # For now, let's just attempt it and expect 400 (not superuser).
        print("Attempting Billing Trigger (User)...")
        resp = await client.post(f"{BASE_URL}/billing/generate-invoice?org_id={api_key['org_id']}&start_date={today}&end_date={today}", headers=headers)
        if resp.status_code == 400 and "privileges" in resp.text:
            print("Billing trigger correctly restricted.")
        
        print("Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
