"""Quick test script to validate all major API endpoints."""
import requests
import json

BASE = "http://127.0.0.1:8001/api/v1"

def pp(label, r):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Body: {json.dumps(r.json(), indent=2, default=str)[:500]}")
    except:
        print(f"  Body: {r.text[:300]}")

# 1. Login as SUPER_ADMIN
r = requests.post(f"{BASE}/auth/login", json={"email": "super@demo.com", "password": "Admin@123"})
pp("LOGIN SUPER_ADMIN", r)
super_token = r.json()["access_token"]
super_headers = {"Authorization": f"Bearer {super_token}"}

# 2. List tenants
r = requests.get(f"{BASE}/saas/tenants", headers=super_headers)
pp("LIST TENANTS", r)
tenants = r.json()["data"]
tenant1_id = tenants[0]["id"]

# 3. Platform stats
r = requests.get(f"{BASE}/saas/platform/stats", headers=super_headers)
pp("PLATFORM STATS", r)

# 4. Login as TENANT_ADMIN
r = requests.post(f"{BASE}/auth/login", json={"email": "tenant1@demo.com", "password": "Admin@123"})
pp("LOGIN TENANT_ADMIN", r)
tenant_token = r.json()["access_token"]
tenant_headers = {"Authorization": f"Bearer {tenant_token}"}

# 5. Tenant stats
r = requests.get(f"{BASE}/tenant/stats", headers=tenant_headers)
pp("TENANT STATS", r)

# 6. List services
r = requests.get(f"{BASE}/services", headers=tenant_headers)
pp("LIST SERVICES", r)
services = r.json()["data"]

# 7. List appointments
r = requests.get(f"{BASE}/appointments", headers=tenant_headers)
pp("LIST APPOINTMENTS", r)

# 8. Login as CUSTOMER
r = requests.post(f"{BASE}/auth/login", json={"email": "customer1@demo.com", "password": "Admin@123"})
pp("LOGIN CUSTOMER", r)
cust_token = r.json()["access_token"]
cust_headers = {"Authorization": f"Bearer {cust_token}"}

# 9. Browse public services
r = requests.get(f"{BASE}/public/services", params={"tenant_id": tenant1_id})
pp("PUBLIC SERVICES", r)

# 10. My bookings
r = requests.get(f"{BASE}/bookings/my", headers=cust_headers)
pp("MY BOOKINGS", r)

# 11. Create a new booking
if services:
    svc_id = services[0]["id"]
    r = requests.post(f"{BASE}/bookings", json={
        "service_id": svc_id,
        "start_at": "2026-03-01T10:00:00Z",
    }, headers=cust_headers)
    pp("CREATE BOOKING", r)
    
    if r.status_code == 200:
        booking_id = r.json()["data"]["id"]
        
        # 12. Start payment
        r = requests.post(f"{BASE}/payments/start", json={
            "appointment_id": booking_id,
        }, headers=cust_headers)
        pp("START PAYMENT", r)
        
        if r.status_code == 200:
            payment_id = r.json()["data"]["id"]
            
            # 13. Verify payment
            r = requests.post(f"{BASE}/payments/verify", json={
                "payment_id": payment_id,
                "otp": "1234",
            }, headers=cust_headers)
            pp("VERIFY PAYMENT", r)

# 14. Tenant stats after payment
r = requests.get(f"{BASE}/tenant/stats", headers=tenant_headers)
pp("TENANT STATS (AFTER)", r)

print("\n" + "="*60)
print("  ALL TESTS COMPLETED!")
print("="*60)
