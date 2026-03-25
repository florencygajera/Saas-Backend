"""Quick test script to validate all major API endpoints."""

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


def pp(label, r):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Status: {r.status_code}")
    try:
        print(f"  Body: {json.dumps(r.json(), indent=2, default=str)[:500]})")
    except Exception:
        print(f"  Body: {r.text[:300]}")


def skip_if_no_server():
    """Decorator to skip test if server is not available."""
    if not is_server_available():
        pytest.skip("Server not running on port 8001")


@pytest.fixture
def super_headers():
    """1. Login as SUPER_ADMIN"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login", json={"email": "super@demo.com", "password": "Admin@123"}
    )
    pp("LOGIN SUPER_ADMIN", r)
    assert r.status_code == 200
    super_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {super_token}"}


@pytest.fixture
def tenant_headers(super_headers):
    """2. Login as TENANT_ADMIN"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "tenant1@demo.com", "password": "Admin@123"},
    )
    pp("LOGIN TENANT_ADMIN", r)
    assert r.status_code == 200
    tenant_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {tenant_token}"}


@pytest.fixture
def tenant_id(super_headers):
    """Get tenant ID from list"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/saas/tenants", headers=super_headers)
    pp("LIST TENANTS", r)
    assert r.status_code == 200
    tenants = r.json()["data"]
    return tenants[0]["id"]


def test_login_super_admin(super_headers):
    """1. Login as SUPER_ADMIN - already done in fixture"""
    assert super_headers is not None


def test_list_tenants(super_headers):
    """2. List tenants"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/saas/tenants", headers=super_headers)
    pp("LIST TENANTS", r)
    assert r.status_code == 200


def test_platform_stats(super_headers):
    """3. Platform stats"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/saas/platform/stats", headers=super_headers)
    pp("PLATFORM STATS", r)
    assert r.status_code == 200


def test_tenant_stats(tenant_headers):
    """4. Tenant stats"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/tenant/stats", headers=tenant_headers)
    pp("TENANT STATS", r)
    assert r.status_code == 200


def test_list_services(tenant_headers):
    """5. List services"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/services", headers=tenant_headers)
    pp("LIST SERVICES", r)
    assert r.status_code == 200


def test_list_appointments(tenant_headers):
    """6. List appointments"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/appointments", headers=tenant_headers)
    pp("LIST APPOINTMENTS", r)
    assert r.status_code == 200


@pytest.fixture
def cust_headers():
    """7. Login as CUSTOMER"""
    skip_if_no_server()
    r = requests.post(
        f"{BASE}/auth/login",
        json={"email": "customer1@demo.com", "password": "Admin@123"},
    )
    pp("LOGIN CUSTOMER", r)
    assert r.status_code == 200
    cust_token = r.json()["access_token"]
    return {"Authorization": f"Bearer {cust_token}"}


def test_public_services(tenant_id):
    """8. Browse public services"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/public/services", params={"tenant_id": tenant_id})
    pp("PUBLIC SERVICES", r)
    assert r.status_code == 200


def test_my_bookings(cust_headers):
    """9. My bookings"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/bookings/my", headers=cust_headers)
    pp("MY BOOKINGS", r)
    assert r.status_code == 200


def test_create_booking(tenant_headers, cust_headers):
    """10. Create a new booking"""
    skip_if_no_server()
    # First get services
    r = requests.get(f"{BASE}/services", headers=tenant_headers)
    pp("LIST SERVICES", r)
    services = r.json()["data"]

    if services:
        svc_id = services[0]["id"]
        r = requests.post(
            f"{BASE}/bookings",
            json={"service_id": svc_id, "start_at": "2026-03-01T10:00:00Z"},
            headers=cust_headers,
        )
        pp("CREATE BOOKING", r)
        assert r.status_code == 200


def test_tenant_stats_after(tenant_headers):
    """11. Tenant stats after operations"""
    skip_if_no_server()
    r = requests.get(f"{BASE}/tenant/stats", headers=tenant_headers)
    pp("TENANT STATS (AFTER)", r)
    assert r.status_code == 200
