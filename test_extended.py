"""Extended test: status transitions, forbidden access, tenant isolation."""

import pytest
import requests
import json

BASE = "http://127.0.0.1:8001/api/v1"


def is_server_available():
    """Check if the server is running."""
    try:
        requests.post(
            f"{BASE}/auth/login", json={"email": "test", "password": "test"}, timeout=2
        )
        return True
    except Exception:
        return False


def skip_if_no_server():
    """Decorator to skip test if server is not available."""
    if not is_server_available():
        pytest.skip("Server not running on port 8001")


def pp(label, r):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Body: {json.dumps(r.json(), indent=2, default=str)[:400]})")
    except Exception:
        print(f"  Body: {r.text[:300]}")


@pytest.fixture
def super_h():
    """Login as SUPER_ADMIN"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login", json={"email": "super@demo.com", "password": "Admin@123"}
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def t1_h():
    """Login as TENANT1"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "tenant1@demo.com", "password": "Admin@123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def t2_h():
    """Login as TENANT2"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "tenant2@demo.com", "password": "Admin@123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def c1_h():
    """Login as CUSTOMER"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "customer1@demo.com", "password": "Admin@123"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_all_logins(super_h, t1_h, t2_h, c1_h):
    """All logins successful"""
    print("[OK] All logins successful")
    assert super_h is not None
    assert t1_h is not None
    assert t2_h is not None
    assert c1_h is not None


def test_tenant_isolation_t2_services(t2_h):
    """=== Test 1: Tenant isolation - T2 can't see T1's services ==="""
    skip_if_no_server()
    r = requests.get(f"{BASE}/services", headers=t2_h)
    pp("T2 SERVICES (should be gym services only)", r)
    assert r.status_code == 200
    services = r.json()["data"]
    # T2 should only see their own services (Gym, Training, etc.)
    for svc in services:
        name = svc["name"]
        assert (
            "Gym" in name or "Training" in name or "Yoga" in name or "CrossFit" in name
        ), f"Unexpected service: {name}"
    print("  [PASS] Tenant isolation confirmed")


def test_customer_cannot_access_admin(c1_h):
    """=== Test 2: Customer can't access admin endpoints ==="""
    skip_if_no_server()
    r = requests.get(f"{BASE}/services", headers=c1_h)
    pp("CUSTOMER tries admin endpoint", r)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  [PASS] Customer blocked from admin endpoint")


def test_status_transitions(t1_h):
    """=== Test 3: Status transitions ==="""
    skip_if_no_server()
    # Get a PENDING appointment
    r = requests.get(f"{BASE}/appointments", headers=t1_h)
    appts = r.json()["data"]
    pending = [a for a in appts if a["status"] == "PENDING"]

    if not pending:
        pytest.skip("No PENDING appointments found")

    appt_id = pending[0]["id"]

    # T1 Admin: PENDING -> CONFIRMED
    r = requests.patch(
        f"{BASE}/appointments/{appt_id}/status",
        headers=t1_h,
        json={"new_status": "CONFIRMED"},
    )
    pp("PENDING -> CONFIRMED", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "CONFIRMED"
    print("  [PASS]")

    # T1 Admin: CONFIRMED -> IN_PROGRESS
    r = requests.patch(
        f"{BASE}/appointments/{appt_id}/status",
        headers=t1_h,
        json={"new_status": "IN_PROGRESS"},
    )
    pp("CONFIRMED -> IN_PROGRESS", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "IN_PROGRESS"
    print("  [PASS]")

    # T1 Admin: IN_PROGRESS -> COMPLETED
    r = requests.patch(
        f"{BASE}/appointments/{appt_id}/status",
        headers=t1_h,
        json={"new_status": "COMPLETED"},
    )
    pp("IN_PROGRESS -> COMPLETED", r)
    assert r.status_code == 200 and r.json()["data"]["status"] == "COMPLETED"
    print("  [PASS]")

    # T1 Admin: COMPLETED -> anything (should fail)
    r = requests.patch(
        f"{BASE}/appointments/{appt_id}/status",
        headers=t1_h,
        json={"new_status": "PENDING"},
    )
    pp("COMPLETED -> PENDING (should fail)", r)
    assert r.status_code == 400
    print("  [PASS] Terminal state enforced")


def test_super_admin_provision(super_h):
    """=== Test 4: Super admin provision ==="""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/saas/tenants",
        headers=super_h,
        json={
            "name": "Test Spa",
            "plan": "basic",
            "admin_name": "Spa Boss",
            "admin_email": "spa@test.com",
            "subscription_price": 19.99,
        },
    )
    pp("PROVISION NEW TENANT", r)
    assert r.status_code == 200
    print("  [PASS] Tenant provisioned")


def test_super_admin_disable_tenant(super_h):
    """=== Test 5: Super admin disable tenant ==="""
    skip_if_no_server()
    # First create a tenant
    r = requests.post(
        f"{BASE}/saas/tenants",
        headers=super_h,
        json={
            "name": "Test Spa Disable",
            "plan": "basic",
            "admin_name": "Spa Boss",
            "admin_email": "spadisable@test.com",
            "subscription_price": 19.99,
        },
    )
    assert r.status_code == 200
    new_tenant_id = r.json()["data"]["tenant"]["id"]

    r = requests.patch(
        f"{BASE}/saas/tenants/{new_tenant_id}",
        headers=super_h,
        json={"is_active": False},
    )
    pp("DISABLE TENANT", r)
    assert r.status_code == 200 and not r.json()["data"]["is_active"]
    print("  [PASS] Tenant disabled")


def test_auth_me(c1_h):
    """=== Test 6: Auth/me ==="""
    skip_if_no_server()
    r = requests.get(f"{BASE}/auth/me", headers=c1_h)
    pp("AUTH/ME (customer)", r)
    assert r.status_code == 200
    print("  [PASS]")
