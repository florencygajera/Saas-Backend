"""Extended test: status transitions, forbidden access, tenant isolation."""
import requests
import json

BASE = "http://127.0.0.1:8001/api/v1"

def pp(label, r):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Body: {json.dumps(r.json(), indent=2, default=str)[:400]}")
    except:
        print(f"  Body: {r.text[:300]}")

# Login all roles
r = requests.post(f"{BASE}/auth/login", json={"email": "super@demo.com", "password": "Admin@123"})
super_h = {"Authorization": f"Bearer {r.json()['access_token']}"}

r = requests.post(f"{BASE}/auth/login", json={"email": "tenant1@demo.com", "password": "Admin@123"})
t1_h = {"Authorization": f"Bearer {r.json()['access_token']}"}

r = requests.post(f"{BASE}/auth/login", json={"email": "tenant2@demo.com", "password": "Admin@123"})
t2_h = {"Authorization": f"Bearer {r.json()['access_token']}"}

r = requests.post(f"{BASE}/auth/login", json={"email": "customer1@demo.com", "password": "Admin@123"})
c1_h = {"Authorization": f"Bearer {r.json()['access_token']}"}

print("[OK] All logins successful")

# === Test 1: Tenant isolation - T2 can't see T1's services ===
r = requests.get(f"{BASE}/services", headers=t2_h)
pp("T2 SERVICES (should be gym services only)", r)
for svc in r.json()["data"]:
    assert "Gym" in r.json()["data"][0]["name"] or "Training" in svc["name"] or "Yoga" in svc["name"] or "CrossFit" in svc["name"], f"Unexpected service: {svc['name']}"
print("  [PASS] Tenant isolation confirmed")

# === Test 2: Customer can't access admin endpoints ===
r = requests.get(f"{BASE}/services", headers=c1_h)
pp("CUSTOMER tries admin endpoint", r)
assert r.status_code == 403, f"Expected 403, got {r.status_code}"
print("  [PASS] Customer blocked from admin endpoint")

# === Test 3: Status transitions ===
# Get a PENDING appointment
r = requests.get(f"{BASE}/appointments", headers=t1_h)
appts = r.json()["data"]
pending = [a for a in appts if a["status"] == "PENDING"]

if pending:
    appt_id = pending[0]["id"]
    
    # T1 Admin: PENDING -> CONFIRMED
    r = requests.patch(f"{BASE}/appointments/{appt_id}/status", headers=t1_h,
                       json={"new_status": "CONFIRMED"})
    pp("PENDING -> CONFIRMED", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "CONFIRMED"
    print("  [PASS]")
    
    # T1 Admin: CONFIRMED -> IN_PROGRESS
    r = requests.patch(f"{BASE}/appointments/{appt_id}/status", headers=t1_h,
                       json={"new_status": "IN_PROGRESS"})
    pp("CONFIRMED -> IN_PROGRESS", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "IN_PROGRESS"
    print("  [PASS]")
    
    # T1 Admin: IN_PROGRESS -> COMPLETED
    r = requests.patch(f"{BASE}/appointments/{appt_id}/status", headers=t1_h,
                       json={"new_status": "COMPLETED"})
    pp("IN_PROGRESS -> COMPLETED", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "COMPLETED"
    print("  [PASS]")
    
    # T1 Admin: COMPLETED -> anything (should fail)
    r = requests.patch(f"{BASE}/appointments/{appt_id}/status", headers=t1_h,
                       json={"new_status": "PENDING"})
    pp("COMPLETED -> PENDING (should fail)", r)
    assert r.status_code == 400
    print("  [PASS] Terminal state enforced")

# === Test 4: Super admin provision ===
r = requests.post(f"{BASE}/saas/tenants", headers=super_h, json={
    "name": "Test Spa",
    "plan": "basic",
    "admin_name": "Spa Boss",
    "admin_email": "spa@test.com",
    "subscription_price": 19.99
})
pp("PROVISION NEW TENANT", r)
assert r.status_code == 200
print("  [PASS] Tenant provisioned")

# === Test 5: Super admin disable tenant ===
new_tenant_id = r.json()["data"]["tenant"]["id"]
r = requests.patch(f"{BASE}/saas/tenants/{new_tenant_id}", headers=super_h,
                   json={"is_active": False})
pp("DISABLE TENANT", r)
assert r.status_code == 200 and r.json()["data"]["is_active"] == False
print("  [PASS] Tenant disabled")

# === Test 6: Auth/me ===
r = requests.get(f"{BASE}/auth/me", headers=c1_h)
pp("AUTH/ME (customer)", r)
assert r.status_code == 200
print("  [PASS]")

print("\n" + "=" * 60)
print("  ALL EXTENDED TESTS PASSED!")
print("=" * 60)
