from flask import Blueprint

from app.models import PlanAbonnement


plans_bp = Blueprint("plans", __name__)


def plan_to_dict(plan):
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "price": str(plan.price),
        "billing_period": plan.billing_period.value,
        "max_users": plan.max_users,
        "max_orders": plan.max_orders,
        "features": {
            "advanced_reports": plan.advanced_reports,
            "online_payment": plan.online_payment,
        },
    }


@plans_bp.get("")
def list_plans():
    plans = (
        PlanAbonnement.query
        .filter_by(is_active=True)
        .order_by(PlanAbonnement.price.asc())
        .all()
    )

    return {"items": [plan_to_dict(plan) for plan in plans]}, 200
