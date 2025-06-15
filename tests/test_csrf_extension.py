from __future__ import annotations

import pytest
from flask import Blueprint
from flask import Flask
from flask import g
from flask import render_template_string
from flask.ctx import AppContext
from flask.ctx import RequestContext
from flask.testing import FlaskClient
from flask.wrappers import Response

from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf


@pytest.fixture
def app(app: Flask) -> Flask:
    CSRFProtect(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        pass

    @app.after_request
    def add_csrf_header(response: Response) -> Response:
        response.headers.set("X-CSRF-Token", generate_csrf())
        return response

    return app


@pytest.fixture
def csrf(app: Flask) -> CSRFProtect:
    return app.extensions["csrf"]


def test_render_token(req_ctx: RequestContext) -> None:
    token = generate_csrf()
    assert render_template_string("{{ csrf_token() }}") == token


def test_protect(app: Flask, client: FlaskClient, app_ctx: AppContext) -> None:
    response = client.post("/")
    assert response.status_code == 400
    assert "The CSRF token is missing." in response.get_data(as_text=True)

    app.config["WTF_CSRF_ENABLED"] = False
    assert client.post("/").get_data() == b""
    app.config["WTF_CSRF_ENABLED"] = True

    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    assert client.post("/").get_data() == b""
    app.config["WTF_CSRF_CHECK_DEFAULT"] = True

    assert client.options("/").status_code == 200
    assert client.post("/not-found").status_code == 404

    response = client.get("/")
    assert response.status_code == 200
    token = response.headers["X-CSRF-Token"]
    assert client.post("/", data={"csrf_token": token}).status_code == 200
    assert client.post("/", data={"prefix-csrf_token": token}).status_code == 200
    assert client.post("/", data={"prefix-csrf_token": ""}).status_code == 400
    assert client.post("/", headers={"X-CSRF-Token": token}).status_code == 200


def test_same_origin(client: FlaskClient) -> None:
    token = client.get("/").headers["X-CSRF-Token"]
    response = client.post(
        "/", base_url="https://localhost", headers={"X-CSRF-Token": token}
    )
    data = response.get_data(as_text=True)
    assert "The referrer header is missing." in data

    response = client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "http://localhost/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://other/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost:8080/"},
    )
    data = response.get_data(as_text=True)
    assert "The referrer does not match the host." in data

    response = client.post(
        "/",
        base_url="https://localhost",
        headers={"X-CSRF-Token": token, "Referer": "https://localhost/"},
    )
    assert response.status_code == 200


def test_form_csrf_short_circuit(app: Flask, client: FlaskClient) -> None:
    @app.route("/skip", methods=["POST"])
    def skip():
        assert g.get("csrf_valid")
        # don't pass the token, then validate the form
        # this would fail if CSRFProtect didn't run
        form: FlaskForm = FlaskForm(None)
        assert form.validate()

    token = client.get("/").headers["X-CSRF-Token"]
    response = client.post("/skip", headers={"X-CSRF-Token": token})
    assert response.status_code == 200


def test_exempt_view(app: Flask, csrf: CSRFProtect, client: FlaskClient) -> None:
    @app.route("/exempt", methods=["POST"])
    @csrf.exempt
    def exempt():
        pass

    response = client.post("/exempt")
    assert response.status_code == 200

    csrf.exempt("test_csrf_extension.index")
    response = client.post("/")
    assert response.status_code == 200


def test_manual_protect(app: Flask, csrf: CSRFProtect, client: FlaskClient) -> None:
    @app.route("/manual", methods=["GET", "POST"])
    @csrf.exempt
    def manual():
        csrf.protect()

    response = client.get("/manual")
    assert response.status_code == 200

    response = client.post("/manual")
    assert response.status_code == 400


def test_exempt_blueprint(app: Flask, csrf: CSRFProtect, client: FlaskClient) -> None:
    bp = Blueprint("exempt", __name__, url_prefix="/exempt")
    csrf.exempt(bp)

    @bp.route("/", methods=["POST"])
    def index():
        pass

    app.register_blueprint(bp)
    response = client.post("/exempt/")
    assert response.status_code == 200


def test_exempt_nested_blueprint(
    app: Flask, csrf: CSRFProtect, client: FlaskClient
) -> None:
    bp1 = Blueprint("exempt1", __name__, url_prefix="/")
    bp2 = Blueprint("exempt2", __name__, url_prefix="/exempt")
    csrf.exempt(bp2)

    @bp2.route("/", methods=["POST"])
    def index():
        pass

    bp1.register_blueprint(bp2)
    app.register_blueprint(bp1)

    response = client.post("/exempt/")
    assert response.status_code == 200


def test_error_handler(app: Flask, client: FlaskClient) -> None:
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e: CSRFError) -> str:
        return e.description.lower()

    response = client.post("/")
    assert response.get_data(as_text=True) == "the csrf token is missing."


def test_validate_error_logged(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from flask_wtf.csrf import logger

    messages: list[str] = []

    def assert_info(message: str) -> None:
        messages.append(message)

    monkeypatch.setattr(logger, "info", assert_info)

    client.post("/")
    assert len(messages) == 1
    assert messages[0] == "The CSRF token is missing."
