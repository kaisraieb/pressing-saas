import calendar

from app.extensions import db
from app.models import Abonnement, PlanAbonnement, SubscriptionStatus, utc_now


class SubscriptionService:
    active_statuses = (
        SubscriptionStatus.TRIALING,
        SubscriptionStatus.ACTIVE,
    )

    def create_subscription(self, tenant_id, plan_id):
        plan = PlanAbonnement.query.filter_by(
            id=plan_id,
            is_active=True,
        ).first()
        if plan is None:
            raise ValueError("PLAN_NOT_FOUND")

        current = Abonnement.query.filter(
            Abonnement.tenant_id == tenant_id,
            Abonnement.status.in_(self.active_statuses),
        ).first()
        if current is not None:
            raise ValueError("ACTIVE_SUBSCRIPTION_EXISTS")

        start = utc_now()
        subscription = Abonnement(
            tenant_id=tenant_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            started_at=start,
            current_period_start=start,
            current_period_end=self._period_end(start, plan.billing_period.value),
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def _period_end(start, billing_period):
        if billing_period == "YEARLY":
            year = start.year + 1
            day = min(start.day, calendar.monthrange(year, start.month)[1])
            return start.replace(year=year, day=day)
        month = start.month + 1
        year = start.year
        if month == 13:
            month = 1
            year += 1
        day = min(start.day, calendar.monthrange(year, month)[1])
        return start.replace(year=year, month=month, day=day)
