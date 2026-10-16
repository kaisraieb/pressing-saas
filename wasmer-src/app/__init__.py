from flask import Flask

from config import Config
from app.extensions import cors, db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins="https://frontend.majd-sassi-dev.workers.dev")

    app.config["AUTH_JWKS_URL"] = app.config.get(
        "AUTH_JWKS_URL",
        "https://auth.majd-sassi-dev.workers.dev/api/auth/jwks",
    )

    from app.models import subscription  # noqa: F401
    from app.routes import plans_bp, subscriptions_bp

    app.register_blueprint(plans_bp, url_prefix="/api/plans")
    app.register_blueprint(
        subscriptions_bp,
        url_prefix="/api/subscriptions",
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app