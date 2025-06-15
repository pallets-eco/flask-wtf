from __future__ import annotations

import pytest
from flask import Flask
from flask import g
from flask import session
from flask.ctx import AppContext
from flask.ctx import RequestContext
from flask.testing import FlaskClient
from wtforms import ValidationError

from flask_wtf import FlaskForm
from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import validate_csrf


def test_csrf_requires_secret_key(app: Flask, req_ctx: RequestContext) -> None:
    # use secret key set by test setup
    generate_csrf()
    # fail with no key
    app.secret_key = None
    pytest.raises(RuntimeError, generate_csrf)
    # use WTF_CSRF config
    app.config["WTF_CSRF_SECRET_KEY"] = "wtf_secret"
    generate_csrf()
    del app.config["WTF_CSRF_SECRET_KEY"]
    # use direct argument
    generate_csrf(secret_key="direct")


def test_token_stored_by_generate(req_ctx: RequestContext) -> None:
    generate_csrf()
    assert "csrf_token" in session
    assert "csrf_token" in g


def test_custom_token_key(req_ctx: RequestContext) -> None:
    generate_csrf(token_key="oauth_token")
    assert "oauth_token" in session
    assert "oauth_token" in g


def test_token_cached(req_ctx: RequestContext) -> None:
    assert generate_csrf() == generate_csrf()


def test_validate(req_ctx: RequestContext) -> None:
    validate_csrf(generate_csrf())


def test_validation_errors(req_ctx: RequestContext) -> None:
    e = pytest.raises(ValidationError, validate_csrf, None)
    assert str(e.value) == "The CSRF token is missing."

    e = pytest.raises(ValidationError, validate_csrf, "no session")
    assert str(e.value) == "The CSRF session token is missing."

    token = generate_csrf()
    e = pytest.raises(ValidationError, validate_csrf, token, time_limit=-1)
    assert str(e.value) == "The CSRF token has expired."

    e = pytest.raises(ValidationError, validate_csrf, "invalid")
    assert str(e.value) == "The CSRF token is invalid."

    other_token = generate_csrf(token_key="other_csrf")
    e = pytest.raises(ValidationError, validate_csrf, other_token)
    assert str(e.value) == "The CSRF tokens do not match."


def test_form_csrf(app: Flask, client: FlaskClient, app_ctx: AppContext) -> None:
    @app.route("/", methods=["GET", "POST"])
    def index():
        f: FlaskForm = FlaskForm()

        if f.validate_on_submit():
            return "good"

        if f.errors:
            return f.csrf_token.errors[0]

        return f.csrf_token.current_token

    response = client.get("/")
    assert response.get_data(as_text=True) == g.csrf_token

    response = client.post("/")
    assert response.get_data(as_text=True) == "The CSRF token is missing."

    response = client.post("/", data={"csrf_token": g.csrf_token})
    assert response.get_data(as_text=True) == "good"


def test_validate_error_logged(
    req_ctx: RequestContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    from flask_wtf.csrf import logger

    messages: list[str] = []

    def assert_info(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr(logger, "info", assert_info)
    FlaskForm().validate()
    assert len(messages) == 1
    assert messages[0] == "The CSRF token is missing."
