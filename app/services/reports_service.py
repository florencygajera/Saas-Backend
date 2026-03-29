"""Tenant reports service."""

from datetime import datetime
from io import StringIO, BytesIO
import csv
from uuid import UUID

from app.repositories.payment_repo import PaymentRepository
from app.schemas.reports import TransactionRow


class ReportsService:
    def __init__(self, db):
        self.db = db
        self.payment_repo = PaymentRepository(db)

    def list_transactions(
        self,
        tenant_id: UUID,
        status: str | None = None,
        search: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[TransactionRow], int]:
        skip = (page - 1) * limit
        rows, total = self.payment_repo.list_transactions(
            tenant_id=tenant_id,
            status=status,
            search=search,
            from_dt=from_dt,
            to_dt=to_dt,
            skip=skip,
            limit=limit,
        )
        data = [
            TransactionRow(
                payment_id=p.id,
                appointment_id=a.id,
                customer_name=c.name,
                service_name=s.name,
                amount=float(p.amount),
                currency=p.currency,
                status=p.status,
                date=p.created_at,
            )
            for (p, a, c, s) in rows
        ]
        return data, total

    def export_transactions_csv(self, items: list[TransactionRow]) -> bytes:
        out = StringIO()
        writer = csv.writer(out)
        writer.writerow(
            [
                "payment_id",
                "appointment_id",
                "customer_name",
                "service_name",
                "amount",
                "currency",
                "status",
                "date",
            ]
        )
        for i in items:
            writer.writerow(
                [
                    str(i.payment_id),
                    str(i.appointment_id),
                    i.customer_name,
                    i.service_name,
                    i.amount,
                    i.currency,
                    i.status,
                    i.date.isoformat(),
                ]
            )
        return out.getvalue().encode("utf-8")

    def export_transactions_pdf(self, items: list[TransactionRow]) -> bytes:
        # Minimal PDF-like bytes for lightweight export in this baseline backend.
        lines = ["Transactions Report", ""]
        for i in items:
            lines.append(
                f"{i.date.date()} | {i.customer_name} | {i.service_name} | {i.amount} {i.currency} | {i.status}"
            )
        body = "\n".join(lines).encode("utf-8")
        buffer = BytesIO()
        buffer.write(b"%PDF-1.1\n")
        buffer.write(body)
        buffer.write(b"\n%%EOF")
        return buffer.getvalue()

