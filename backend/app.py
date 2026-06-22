"""DebugMyMind backend — Flask application factory.

Run locally:    python app.py            (or: flask --app app run)
Init schema:    flask --app app db-init
Seed data:      flask --app app seed
Production:     gunicorn app:app
"""
from __future__ import annotations

import click
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt

load_dotenv()


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    jwt.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # Import models so they are registered before create_all / queries.
    import models  # noqa: F401

    from auth import auth_bp
    from problems import problems_bp
    from submissions import submissions_bp
    from profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(problems_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(profile_bp)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="debugmymind-backend")

    _register_jwt_handlers()
    _register_cli(app)
    return app


def _register_jwt_handlers() -> None:
    @jwt.unauthorized_loader
    def _missing_token(reason):
        return jsonify(error="missing or invalid Authorization header"), 401

    @jwt.invalid_token_loader
    def _invalid_token(reason):
        return jsonify(error="invalid token"), 422

    @jwt.expired_token_loader
    def _expired_token(header, payload):
        return jsonify(error="token has expired"), 401


def _register_cli(app: Flask) -> None:
    @app.cli.command("db-init")
    def db_init():
        """Create all tables."""
        db.create_all()
        click.echo("Tables created.")

    @app.cli.command("db-reset")
    def db_reset():
        """Drop and recreate all tables (DEV ONLY — destroys data)."""
        db.drop_all()
        db.create_all()
        click.echo("Tables dropped and recreated.")

    @app.cli.command("seed")
    def seed():
        """Load starter problems + misconception catalog."""
        from seed import run_seed

        run_seed()


# Module-level app for gunicorn ("gunicorn app:app") and `python app.py`.
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
