"""Authentication: signup, login, current-user."""
from __future__ import annotations

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

VALID_ROLES = {"student", "teacher"}


def _token_for(user: User) -> str:
    # identity must be a string; role travels as an additional claim.
    return create_access_token(identity=str(user.id), additional_claims={"role": user.role})


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()

    if not name or not email or not password:
        return jsonify(error="name, email and password are required"), 400
    if role not in VALID_ROLES:
        return jsonify(error=f"role must be one of {sorted(VALID_ROLES)}"), 400
    if len(password) < 6:
        return jsonify(error="password must be at least 6 characters"), 400
    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        return jsonify(error=str(exc)), 400

    if User.query.filter_by(email=email).first():
        return jsonify(error="an account with this email already exists"), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(token=_token_for(user), user=user.to_dict()), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(error="email and password are required"), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify(error="invalid email or password"), 401

    return jsonify(token=_token_for(user), user=user.to_dict()), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify(error="user not found"), 404
    return jsonify(user=user.to_dict()), 200
