from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import BillingPeriod, PlanAbonnement


app = create_app()


def seed_plans():
    plans = [
        PlanAbonnement(
            name="BASIC",
            description="Plan adapte aux petits pressings",
            price=Decimal("29.00"),
            billing_period=BillingPeriod.MONTHLY,
            max_users=3,
            max_orders=100,
            advanced_reports=False,
            online_payment=False,
        ),
        PlanAbonnement(
            name="PRO",
            description="Plan adapte aux pressings en croissance",
            price=Decimal("79.00"),
            billing_period=BillingPeriod.MONTHLY,
            max_users=10,
            max_orders=1000,
            advanced_reports=True,
            online_payment=True,
        ),
        PlanAbonnement(
            name="ENTERPRISE",
            description="Plan avance pour les grandes entreprises",
            price=Decimal("199.00"),
            billing_period=BillingPeriod.YEARLY,
            max_users=None,
            max_orders=None,
            advanced_reports=True,
            online_payment=True,
        ),
    ]

    created = 0

    for plan in plans:
        if PlanAbonnement.query.filter_by(name=plan.name).first() is None:
            db.session.add(plan)
            created += 1

    db.session.commit()
    return created


if __name__ == "__main__":
    with app.app_context():
        created = seed_plans()
        print(f"{created} plan(s) ajoute(s).")
