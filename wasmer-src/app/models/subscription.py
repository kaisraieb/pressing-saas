from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class BillingPeriod(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class SubscriptionStatus(str, Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"


class PlanAbonnement(db.Model):
    __tablename__ = "subscription_plans"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    billing_period = db.Column(
        db.Enum(BillingPeriod),
        nullable=False,
    )
    max_users = db.Column(db.Integer, nullable=True)
    max_orders = db.Column(db.Integer, nullable=True)
    advanced_reports = db.Column(db.Boolean, nullable=False, default=False)
    online_payment = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    subscriptions = db.relationship(
        "Abonnement",
        back_populates="plan",
    )


class Abonnement(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    plan_id = db.Column(
        db.String(36),
        db.ForeignKey("subscription_plans.id"),
        nullable=False,
    )
    status = db.Column(
        db.Enum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.TRIALING,
    )
    started_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    current_period_start = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    current_period_end = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    auto_renew = db.Column(db.Boolean, nullable=False, default=True)

    plan = db.relationship(
        "PlanAbonnement",
        back_populates="subscriptions",
    )