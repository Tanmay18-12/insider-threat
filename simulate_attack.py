import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def simulate_attack():
    print("[*] Starting Simulated Attack...")
    
    # 1. Login to get JWT Token
    print("[*] Authenticating as admin...")
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'Admin123!'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data)
    
    try:
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode())
            token = token_data['access_token']
    except Exception as e:
        print(f"[!] Failed to login: {e}")
        return

    # 2. Fetch users to target one
    print("[*] Selecting a target user...")
    req = urllib.request.Request(f"{BASE_URL}/users", headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req) as response:
        users = json.loads(response.read().decode())
        target_user = users[1] # Pick the first non-admin user
        print(f"   -> Targeted User: {target_user['username']} (ID: {target_user['id']})")

    # 3. Send Malicious Payload (Privilege Escalation)
    print("\n[*] Injecting High-Risk Activity (Privilege Escalation)...")
    payload = {
        "user_id": target_user['id'],
        "event_type": "PRIVILEGE_ESCALATION",
        "resource_accessed": "admin/shadow_passwords.txt",
        "ip_address": "185.15.59.224", # Suspicious IP
        "metadata_": {"action": "sudo su", "bypassed_mfa": True}
    }
    
    req = urllib.request.Request(
        f"{BASE_URL}/logs/ingest", 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print(f"[+] Attack Successful! Risk Score Generated: {result['risk_score']:.2f}/100")
        print(f"[!] Alert Created: {result['alert_created']}")
        
    print("\n[+] Check your React Dashboard! You should see a red popup in the top right,")
    print(f"    and {target_user['username']}'s risk score should have spiked!")

if __name__ == "__main__":
    simulate_attack()
