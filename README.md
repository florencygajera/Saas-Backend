# SaaS CRM + Booking System Backend

> Production-ready multi-tenant CRM + Booking API with 3 interfaces (SUPER_ADMIN, TENANT_ADMIN, CUSTOMER)

## Quick Start

### 1. Create Virtual Environment & Install
```bash
cd d:\Project\Saas-Backend\Saas-Backend
python -m venv venv
.\venv\Scripts\pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic pydantic pydantic-settings python-jose[cryptography] passlib bcrypt python-multipart python-dotenv email-validator
```

### 2. Configure Environment
```bash
# Edit .env file — set your DATABASE_URL and JWT_SECRET
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saas_crm
JWT_SECRET=your-secret-key-here
```

### 3. Create Database
```bash
# Using psql (adjust path for your PostgreSQL version)
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -c "CREATE DATABASE saas_crm;"
```

### 4. Run Migrations
```bash
.\venv\Scripts\python -m alembic upgrade head
```

### 5. Seed Demo Data
```bash
.\venv\Scripts\python -m app.scripts.seed
```

### 6. Start Server
```bash
.\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

API docs available at: **http://127.0.0.1:8001/docs**

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| SUPER_ADMIN | `super@demo.com` | `Admin@123` |
| TENANT_ADMIN | `tenant1@demo.com` | `Admin@123` |
| TENANT_ADMIN | `tenant2@demo.com` | `Admin@123` |
| CUSTOMER | `customer1@demo.com` | `Admin@123` |
| CUSTOMER | `customer2@demo.com` | `Admin@123` |

---

## Example curl Requests

### Login (all roles)
```bash
# Super Admin
curl -X POST http://127.0.0.1:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"super@demo.com","password":"Admin@123"}'

# Tenant Admin
curl -X POST http://127.0.0.1:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tenant1@demo.com","password":"Admin@123"}'

# Customer
curl -X POST http://127.0.0.1:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer1@demo.com","password":"Admin@123"}'
```

### Provision a New Tenant (Super Admin)
```bash
curl -X POST http://127.0.0.1:8001/api/v1/saas/tenants \
  -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Zen Spa",
    "plan": "premium",
    "admin_name": "Spa Admin",
    "admin_email": "spa@demo.com",
    "subscription_price": 49.99
  }'
```

### Customer Booking + Payment Flow
```bash
# 1. Browse services (public, no auth)
curl "http://127.0.0.1:8001/api/v1/public/services?tenant_id=<TENANT_ID>"

# 2. Create booking
curl -X POST http://127.0.0.1:8001/api/v1/bookings \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"service_id":"<SERVICE_ID>","start_at":"2026-03-01T10:00:00Z"}'

# 3. Start payment
curl -X POST http://127.0.0.1:8001/api/v1/payments/start \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id":"<APPOINTMENT_ID>"}'

# 4. Verify payment (any 4-digit OTP)
curl -X POST http://127.0.0.1:8001/api/v1/payments/verify \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"payment_id":"<PAYMENT_ID>","otp":"1234"}'
```

### Tenant Stats
```bash
curl http://127.0.0.1:8001/api/v1/tenant/stats \
  -H "Authorization: Bearer <TENANT_ADMIN_TOKEN>"
```

### Platform Stats (Super Admin)
```bash
curl http://127.0.0.1:8001/api/v1/saas/platform/stats \
  -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>"
```

---

## API Endpoints Reference

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | None | Login, returns JWT |
| GET | `/api/v1/auth/me` | Any | Current user info |

### Super Admin (SaaS Owner)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/saas/tenants` | SUPER_ADMIN | Provision tenant + admin |
| GET | `/api/v1/saas/tenants` | SUPER_ADMIN | List all tenants |
| PATCH | `/api/v1/saas/tenants/{id}` | SUPER_ADMIN | Enable/disable tenant |
| GET | `/api/v1/saas/platform/stats` | SUPER_ADMIN | Platform analytics |
| GET | `/api/v1/saas/tenants/{id}/stats` | SUPER_ADMIN | Specific tenant stats |

### Tenant Admin
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/services` | TENANT_ADMIN | Create service |
| GET | `/api/v1/services` | TENANT_ADMIN | List services |
| GET | `/api/v1/services/{id}` | TENANT_ADMIN | Get service |
| PUT | `/api/v1/services/{id}` | TENANT_ADMIN | Update service |
| DELETE | `/api/v1/services/{id}` | TENANT_ADMIN | Delete service |
| POST | `/api/v1/staff` | TENANT_ADMIN | Create staff |
| GET | `/api/v1/staff` | TENANT_ADMIN | List staff |
| PUT | `/api/v1/staff/{id}` | TENANT_ADMIN | Update staff |
| DELETE | `/api/v1/staff/{id}` | TENANT_ADMIN | Delete staff |
| POST | `/api/v1/customers` | TENANT_ADMIN | Create customer |
| GET | `/api/v1/customers` | TENANT_ADMIN | List customers |
| PUT | `/api/v1/customers/{id}` | TENANT_ADMIN | Update customer |
| DELETE | `/api/v1/customers/{id}` | TENANT_ADMIN | Delete customer |
| GET | `/api/v1/appointments` | TENANT_ADMIN | List all appointments |
| PATCH | `/api/v1/appointments/{id}/status` | TENANT_ADMIN | Transition status |
| GET | `/api/v1/tenant/stats` | TENANT_ADMIN | Tenant analytics |

### Customer
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/public/services?tenant_id=...` | None | Browse services |
| POST | `/api/v1/bookings` | CUSTOMER | Create booking |
| GET | `/api/v1/bookings/my` | CUSTOMER | My bookings |
| PATCH | `/api/v1/bookings/{id}` | CUSTOMER | Reschedule (PENDING only) |
| DELETE | `/api/v1/bookings/{id}` | CUSTOMER | Cancel (PENDING only) |

### Payments
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/payments/start` | Any | Start payment |
| POST | `/api/v1/payments/verify` | Any | Verify with 4-digit OTP |

---

## Appointment Status State Machine

```
PENDING ──→ CONFIRMED ──→ IN_PROGRESS ──→ COMPLETED
  │              │
  └──→ CANCELLED ←┘
```

**CUSTOMER**: Can only cancel PENDING appointments
**TENANT_ADMIN**: Full workflow transitions (see above)
**COMPLETED/CANCELLED**: Terminal states, no further transitions

---

## Architecture

```
app/
├── main.py                 # FastAPI app + CORS
├── core/
│   ├── config.py           # pydantic-settings
│   ├── security.py         # JWT + bcrypt
│   ├── deps.py             # Auth dependencies
│   └── exceptions.py       # HTTP exceptions
├── db/
│   ├── base_class.py       # DeclarativeBase
│   ├── base.py             # Model registry
│   └── session.py          # Engine + SessionLocal
├── models/                 # 9 SQLAlchemy models
├── schemas/                # Pydantic v2 schemas
├── repositories/           # Data access with tenant isolation
├── services/               # Business logic layer
├── api/v1/endpoints/       # Route handlers
└── scripts/seed.py         # Demo data
```

## Security Guarantees

1. **JWT claims**: `user_id`, `role`, `tenant_id` (null for SUPER_ADMIN)
2. **tenant_id NEVER from request body** — always derived from JWT
3. **Every repository query** filters by tenant_id for non-super-admin
4. **Customer ownership** enforced for all booking operations
5. **Role guards** via FastAPI dependencies
6. **bcrypt** password hashing
7. **Proper HTTP status codes**: 401/403/400/404/422
