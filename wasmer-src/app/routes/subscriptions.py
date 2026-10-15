from flask import Blueprint, request
from flask import g

from app.auth import jwt_required
from app.models import Abonnement
from app.services import SubscriptionService


subscriptions_bp = Blueprint("subscriptions", __name__)
subscription_service = SubscriptionService()


def subscription_to_dict(subscription):
    return {
        "id": subscription.id,
        "tenant_id": subscription.tenant_id,
        "plan_id": subscription.plan_id,
        "plan_name": subscription.plan.name,
        "status": subscription.status.value,
        "started_at": subscription.started_at.isoformat(),
        "current_period_start": subscription.current_period_start.isoformat(),
        "current_period_end": subscription.current_period_end.isoformat(),
        "auto_renew": subscription.auto_renew,
    }


@subscriptions_bp.post("")
@jwt_required
def create_subscription():
    data = request.get_json(silent=True) or {}
    tenant_id = g.tenant_id
    plan_id = str(data.get("plan_id", "")).strip()

    if not tenant_id or not plan_id:
        return {
            "error": "VALIDATION_ERROR",
            "message": "plan_id est obligatoire",
        }, 400

    try:
        subscription = subscription_service.create_subscription(
            tenant_id=tenant_id,
            plan_id=plan_id,
        )
    except ValueError as error:
        if str(error) == "PLAN_NOT_FOUND":
            return {
                "error": "PLAN_NOT_FOUND",
                "message": "Le plan est introuvable ou inactif",
            }, 404
        return {
            "error": "ACTIVE_SUBSCRIPTION_EXISTS",
            "message": "Le tenant possede deja un abonnement actif",
        }, 409

    return subscription_to_dict(subscription), 201


def _find_current_subscription(tenant_id):
    subscription = (
        Abonnement.query
        .filter(
            Abonnement.tenant_id == tenant_id,
            Abonnement.status.in_(
                subscription_service.active_statuses
            ),
        )
        .order_by(Abonnement.started_at.desc())
        .first()
    )

    if subscription is None:
        return {
            "error": "SUBSCRIPTION_NOT_FOUND",
            "message": "Aucun abonnement actif pour cette organisation",
        }, 404

    return subscription_to_dict(subscription), 200


@subscriptions_bp.get("/me")
@jwt_required
def get_my_subscription():
    return _find_current_subscription(g.tenant_id)

@subscriptions_bp.get("/<tenant_id>")
@jwt_required
def get_current_subscription(tenant_id):
    if tenant_id != g.tenant_id:
        return {
            "error": "FORBIDDEN",
            "message": "Acces a une autre organisation interdit",
        }, 403

    return _find_current_subscription(tenant_id)