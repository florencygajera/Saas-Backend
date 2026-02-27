"""
Seed script -- populates the database with demo data.

Run: python -m app.scripts.seed
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import base to register all models first
import app.db.base  # noqa: F401

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.models.subscription import Subscription
from app.models.user import User
from app.models.service import Service
from app.models.staff import Staff
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.event import Event


def seed():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).filter(User.email == "super@demo.com").first():
            print("[SKIP] Seed data already exists. Skipping.")
            return

        now = datetime.now(timezone.utc)
        password = hash_password("Admin@123")

        # ================================================================
        # 1. SUPER ADMIN
        # ================================================================
        super_admin = User(
            id=uuid4(),
            tenant_id=None,
            role="SUPER_ADMIN",
            name="Super Admin",
            email="super@demo.com",
            password_hash=password,
            is_active=True,
        )
        db.add(super_admin)
        print("[OK] Created SUPER_ADMIN: super@demo.com / Admin@123")

        # ================================================================
        # 2. TENANT 1 -- Beauty Salon
        # ================================================================
        tenant1_id = uuid4()
        tenant1 = Tenant(id=tenant1_id, name="Glamour Salon", plan="premium", is_active=True)
        db.add(tenant1)

        sub1 = Subscription(
            tenant_id=tenant1_id,
            plan="premium",
            price=49.99,
            status="active",
            start_at=now - timedelta(days=60),
        )
        db.add(sub1)

        admin1 = User(
            id=uuid4(),
            tenant_id=tenant1_id,
            role="TENANT_ADMIN",
            name="Salon Admin",
            email="tenant1@demo.com",
            password_hash=password,
            is_active=True,
        )
        db.add(admin1)
        print("[OK] Created Tenant 1: Glamour Salon -- tenant1@demo.com / Admin@123")

        # Services for tenant 1
        svc1_1 = Service(id=uuid4(), tenant_id=tenant1_id, name="Haircut", duration_min=30, price=25.00)
        svc1_2 = Service(id=uuid4(), tenant_id=tenant1_id, name="Hair Coloring", duration_min=90, price=75.00)
        svc1_3 = Service(id=uuid4(), tenant_id=tenant1_id, name="Manicure", duration_min=45, price=35.00)
        svc1_4 = Service(id=uuid4(), tenant_id=tenant1_id, name="Facial", duration_min=60, price=50.00)
        db.add_all([svc1_1, svc1_2, svc1_3, svc1_4])

        # Staff for tenant 1
        staff1_1 = Staff(id=uuid4(), tenant_id=tenant1_id, name="Alice Johnson")
        staff1_2 = Staff(id=uuid4(), tenant_id=tenant1_id, name="Bob Williams")
        db.add_all([staff1_1, staff1_2])

        # Customer users for tenant 1
        cust1_user = User(
            id=uuid4(),
            tenant_id=tenant1_id,
            role="CUSTOMER",
            name="John Customer",
            email="customer1@demo.com",
            password_hash=password,
            is_active=True,
        )
        db.add(cust1_user)

        cust1 = Customer(
            id=uuid4(),
            tenant_id=tenant1_id,
            user_id=cust1_user.id,
            name="John Customer",
            phone="+1234567890",
            email="customer1@demo.com",
        )
        db.add(cust1)

        cust1b = Customer(
            id=uuid4(),
            tenant_id=tenant1_id,
            name="Jane Walk-in",
            phone="+1987654321",
            email="jane@example.com",
        )
        db.add(cust1b)
        print("[OK] Created Customer: customer1@demo.com / Admin@123 (Tenant 1)")

        # Appointments for tenant 1
        appt1_1 = Appointment(
            id=uuid4(),
            tenant_id=tenant1_id,
            customer_id=cust1.id,
            staff_id=staff1_1.id,
            service_id=svc1_1.id,
            start_at=now - timedelta(days=5, hours=2),
            end_at=now - timedelta(days=5, hours=1, minutes=30),
            status="COMPLETED",
            notes="Regular haircut",
        )
        appt1_2 = Appointment(
            id=uuid4(),
            tenant_id=tenant1_id,
            customer_id=cust1.id,
            staff_id=staff1_2.id,
            service_id=svc1_2.id,
            start_at=now - timedelta(days=3, hours=4),
            end_at=now - timedelta(days=3, hours=2, minutes=30),
            status="COMPLETED",
        )
        appt1_3 = Appointment(
            id=uuid4(),
            tenant_id=tenant1_id,
            customer_id=cust1b.id,
            staff_id=staff1_1.id,
            service_id=svc1_3.id,
            start_at=now + timedelta(days=1, hours=3),
            end_at=now + timedelta(days=1, hours=3, minutes=45),
            status="PENDING",
        )
        appt1_4 = Appointment(
            id=uuid4(),
            tenant_id=tenant1_id,
            customer_id=cust1.id,
            staff_id=staff1_2.id,
            service_id=svc1_4.id,
            start_at=now - timedelta(days=10, hours=1),
            end_at=now - timedelta(days=10),
            status="CANCELLED",
        )
        appt1_5 = Appointment(
            id=uuid4(),
            tenant_id=tenant1_id,
            customer_id=cust1.id,
            staff_id=staff1_1.id,
            service_id=svc1_1.id,
            start_at=now + timedelta(days=2, hours=5),
            end_at=now + timedelta(days=2, hours=5, minutes=30),
            status="CONFIRMED",
        )
        db.add_all([appt1_1, appt1_2, appt1_3, appt1_4, appt1_5])

        # Payments for tenant 1
        pay1_1 = Payment(
            tenant_id=tenant1_id,
            appointment_id=appt1_1.id,
            amount=25.00,
            currency="USD",
            status="PAID",
        )
        pay1_2 = Payment(
            tenant_id=tenant1_id,
            appointment_id=appt1_2.id,
            amount=75.00,
            currency="USD",
            status="PAID",
        )
        pay1_3 = Payment(
            tenant_id=tenant1_id,
            appointment_id=appt1_5.id,
            amount=25.00,
            currency="USD",
            status="PAID",
        )
        db.add_all([pay1_1, pay1_2, pay1_3])

        # ================================================================
        # 3. TENANT 2 -- Fitness Gym
        # ================================================================
        tenant2_id = uuid4()
        tenant2 = Tenant(id=tenant2_id, name="PowerFit Gym", plan="basic", is_active=True)
        db.add(tenant2)

        sub2 = Subscription(
            tenant_id=tenant2_id,
            plan="basic",
            price=29.99,
            status="active",
            start_at=now - timedelta(days=15),
        )
        db.add(sub2)

        admin2 = User(
            id=uuid4(),
            tenant_id=tenant2_id,
            role="TENANT_ADMIN",
            name="Gym Admin",
            email="tenant2@demo.com",
            password_hash=password,
            is_active=True,
        )
        db.add(admin2)
        print("[OK] Created Tenant 2: PowerFit Gym -- tenant2@demo.com / Admin@123")

        # Services for tenant 2
        svc2_1 = Service(id=uuid4(), tenant_id=tenant2_id, name="Personal Training", duration_min=60, price=60.00)
        svc2_2 = Service(id=uuid4(), tenant_id=tenant2_id, name="Yoga Class", duration_min=45, price=20.00)
        svc2_3 = Service(id=uuid4(), tenant_id=tenant2_id, name="CrossFit Session", duration_min=60, price=30.00)
        db.add_all([svc2_1, svc2_2, svc2_3])

        # Staff for tenant 2
        staff2_1 = Staff(id=uuid4(), tenant_id=tenant2_id, name="Mike Trainer")
        staff2_2 = Staff(id=uuid4(), tenant_id=tenant2_id, name="Sarah Coach")
        db.add_all([staff2_1, staff2_2])

        # Customer for tenant 2
        cust2_user = User(
            id=uuid4(),
            tenant_id=tenant2_id,
            role="CUSTOMER",
            name="Dave Lifter",
            email="customer2@demo.com",
            password_hash=password,
            is_active=True,
        )
        db.add(cust2_user)

        cust2 = Customer(
            id=uuid4(),
            tenant_id=tenant2_id,
            user_id=cust2_user.id,
            name="Dave Lifter",
            phone="+1555666777",
            email="customer2@demo.com",
        )
        db.add(cust2)
        print("[OK] Created Customer: customer2@demo.com / Admin@123 (Tenant 2)")

        # Appointments for tenant 2
        appt2_1 = Appointment(
            id=uuid4(),
            tenant_id=tenant2_id,
            customer_id=cust2.id,
            staff_id=staff2_1.id,
            service_id=svc2_1.id,
            start_at=now - timedelta(days=2, hours=6),
            end_at=now - timedelta(days=2, hours=5),
            status="COMPLETED",
        )
        appt2_2 = Appointment(
            id=uuid4(),
            tenant_id=tenant2_id,
            customer_id=cust2.id,
            staff_id=staff2_2.id,
            service_id=svc2_2.id,
            start_at=now + timedelta(days=1, hours=8),
            end_at=now + timedelta(days=1, hours=8, minutes=45),
            status="PENDING",
        )
        appt2_3 = Appointment(
            id=uuid4(),
            tenant_id=tenant2_id,
            customer_id=cust2.id,
            staff_id=staff2_1.id,
            service_id=svc2_3.id,
            start_at=now - timedelta(days=7, hours=3),
            end_at=now - timedelta(days=7, hours=2),
            status="COMPLETED",
        )
        db.add_all([appt2_1, appt2_2, appt2_3])

        # Payments for tenant 2
        pay2_1 = Payment(
            tenant_id=tenant2_id,
            appointment_id=appt2_1.id,
            amount=60.00,
            currency="USD",
            status="PAID",
        )
        pay2_2 = Payment(
            tenant_id=tenant2_id,
            appointment_id=appt2_3.id,
            amount=30.00,
            currency="USD",
            status="PAID",
        )
        db.add_all([pay2_1, pay2_2])

        # Flush all pending inserts before adding events (FK dependencies)
        db.flush()

        # Events
        event1 = Event(
            tenant_id=tenant1_id,
            actor_user_id=admin1.id,
            event_type="TENANT_PROVISIONED",
            meta_json='{"plan": "premium"}',
        )
        event2 = Event(
            tenant_id=tenant2_id,
            actor_user_id=admin2.id,
            event_type="TENANT_PROVISIONED",
            meta_json='{"plan": "basic"}',
        )
        db.add_all([event1, event2])

        db.commit()
        print("")
        print("[DONE] Seed completed successfully!")
        print("=" * 50)
        print("Demo Accounts:")
        print("  SUPER_ADMIN:  super@demo.com / Admin@123")
        print("  TENANT_ADMIN: tenant1@demo.com / Admin@123 (Glamour Salon)")
        print("  TENANT_ADMIN: tenant2@demo.com / Admin@123 (PowerFit Gym)")
        print("  CUSTOMER:     customer1@demo.com / Admin@123 (Salon customer)")
        print("  CUSTOMER:     customer2@demo.com / Admin@123 (Gym customer)")
        print("=" * 50)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
