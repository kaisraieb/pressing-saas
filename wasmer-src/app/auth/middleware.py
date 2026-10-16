from functools import lru_cache, wraps

import jwt
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient


@lru_cache(maxsize=4)
def _jwks_client(jwks_url):
    return PyJWKClient(
        jwks_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "pressing-saas-subscription-service/1.0",
        },
        timeout=10,
    )


def _unauthorized(message):
    return jsonify({
        "error": "UNAUTHORIZED",
        "message": message,
    }), 401


def _organization_id(claims):
    for key in (
        "organization_id",
        "organizationId",
        "business_owner_id",
        "businessOwnerId",
        "tenant_id",
        "tenantId",
    ):
        value = claims.get(key)
        if value:
            return str(value)

    # Simple users do not have an organization claim. Use the verified
    # subject as their tenant identity so their data remains isolated.
    for key in ("sub", "id"):
        value = claims.get(key)
        if value:
            return str(value)

    return None


def jwt_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer" or not token:
            return _unauthorized("Bearer token manquant")

        try:
            jwks_url = current_app.config["AUTH_JWKS_URL"]
            jwks_client = _jwks_client(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            issuer = current_app.config.get("AUTH_JWT_ISSUER")
            audience = current_app.config.get("AUTH_JWT_AUDIENCE")
            decode_options = {
                "algorithms": ["EdDSA"],
                "key": signing_key.key,
                "options": {"verify_aud": audience is not None},
            }
            if issuer:
                decode_options["issuer"] = issuer
            if audience:
                decode_options["audience"] = audience

            claims = jwt.decode(token, **decode_options)
        except jwt.ExpiredSignatureError:
            return _unauthorized("Token expire")
        except jwt.InvalidTokenError as error:
            current_app.logger.warning(
                "Invalid JWT: %s",
                error,
            )
            return _unauthorized("Token invalide")
        except Exception as error:
            current_app.logger.exception(
                "JWT verification failed: %s",
                error,
            )
            return _unauthorized("Impossible de verifier le token")

        organization_id = _organization_id(claims)
        if organization_id is None:
            mock_tenant_id = current_app.config.get("AUTH_MOCK_TENANT_ID")
            if current_app.debug and mock_tenant_id:
                organization_id = mock_tenant_id
                current_app.logger.warning(
                    "Using development mock tenant for JWT subject %s",
                    claims.get("sub"),
                )
            else:
                return _unauthorized(
                    "Le token ne contient pas d'identifiant d'organisation"
                )

        g.jwt_claims = claims
        g.organization_id = organization_id
        g.tenant_id = organization_id
        return function(*args, **kwargs)

    return wrapper
