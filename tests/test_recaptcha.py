import pytest
from flask import json
from markupsafe import Markup

from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from flask_wtf.recaptcha.validators import http
from flask_wtf.recaptcha.validators import Recaptcha


class RecaptchaForm(FlaskForm):
    class Meta:
        csrf = False

    recaptcha = RecaptchaField()


class RecaptchaNonceForm(FlaskForm):
    class Meta:
        csrf = False

    recaptcha = RecaptchaField(nonce="foobar")


class RecaptchaNonceCallableForm(FlaskForm):
    """Form using a callable nonce, for per-request resolution tests."""

    class Meta:
        csrf = False

    recaptcha = RecaptchaField(nonce=lambda: "dynamic-nonce")


class RecaptchaNonceUnsafeForm(FlaskForm):
    """Form with an HTML-unsafe nonce, to assert escaping."""

    class Meta:
        csrf = False

    recaptcha = RecaptchaField(nonce='"><script>alert(1)</script>')


@pytest.fixture
def app(app):
    app.testing = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["RECAPTCHA_PUBLIC_KEY"] = "public"
    app.config["RECAPTCHA_PRIVATE_KEY"] = "private"
    return app


@pytest.fixture(autouse=True)
def req_ctx(app):
    with app.test_request_context(data={"g-recaptcha-response": "pass"}) as ctx:
        yield ctx


def test_config(app, monkeypatch):
    f = RecaptchaForm()
    monkeypatch.setattr(app, "testing", True)
    f.validate()
    assert not f.recaptcha.errors
    monkeypatch.undo()

    monkeypatch.delitem(app.config, "RECAPTCHA_PUBLIC_KEY")
    pytest.raises(RuntimeError, f.recaptcha)
    monkeypatch.undo()

    monkeypatch.delitem(app.config, "RECAPTCHA_PRIVATE_KEY")
    pytest.raises(RuntimeError, f.validate)


def test_render_has_js():
    f = RecaptchaForm()
    render = f.recaptcha()
    assert "https://www.google.com/recaptcha/api.js" in render


def test_render_has_custom_js(app):
    captcha_script = "https://hcaptcha.com/1/api.js"
    app.config["RECAPTCHA_SCRIPT"] = captcha_script
    f = RecaptchaForm()
    render = f.recaptcha()
    assert captcha_script in render


def test_render_has_nonce():
    f = RecaptchaNonceForm()
    render = f.recaptcha()
    assert 'nonce="foobar"' in render


def test_render_without_nonce():
    """Render must not include a nonce attribute when none is set."""
    f = RecaptchaForm()
    render = f.recaptcha()
    assert "nonce=" not in render


def test_render_nonce_callable():
    """A callable nonce is resolved at render time."""
    f = RecaptchaNonceCallableForm()
    render = f.recaptcha()
    assert 'nonce="dynamic-nonce"' in render


def test_render_nonce_is_escaped():
    """Nonce values are HTML-escaped to avoid attribute injection."""
    f = RecaptchaNonceUnsafeForm()
    render = f.recaptcha()
    assert "<script>alert(1)</script>" not in render
    assert "&lt;script&gt;" in render


def test_render_custom_html(app):
    app.config["RECAPTCHA_HTML"] = "custom"
    f = RecaptchaForm()
    render = f.recaptcha()
    assert render == "custom"
    assert isinstance(render, Markup)


def test_render_custom_div_class(app):
    div_class = "h-captcha"
    app.config["RECAPTCHA_DIV_CLASS"] = div_class
    f = RecaptchaForm()
    render = f.recaptcha()
    assert div_class in render


def test_render_custom_args(app):
    app.config["RECAPTCHA_PARAMETERS"] = {"key": "(value)"}
    app.config["RECAPTCHA_DATA_ATTRS"] = {"red": "blue"}
    f = RecaptchaForm()
    render = f.recaptcha()
    assert "?key=(value)" in render or "?key=%28value%29" in render
    assert 'data-red="blue"' in render


def test_render_default_id_from_field():
    """The div ``id`` defaults to the field id."""
    f = RecaptchaForm()
    render = f.recaptcha()
    assert f'id="{f.recaptcha.id}"' in render


def test_render_custom_html_attrs():
    """Arbitrary HTML attributes can be passed as kwargs to the widget."""
    f = RecaptchaForm()
    render = f.recaptcha(style="margin: 1em;", aria_label="captcha")
    assert 'style="margin: 1em;"' in render
    assert 'aria-label="captcha"' in render


def test_render_kwargs_override_class(app):
    """``class_`` kwarg takes precedence over ``RECAPTCHA_DIV_CLASS`` config."""
    app.config["RECAPTCHA_DIV_CLASS"] = "from-config"
    f = RecaptchaForm()
    render = f.recaptcha(class_="from-kwargs")
    assert 'class="from-kwargs"' in render
    assert "from-config" not in render


def test_render_kwargs_override_data_attr(app):
    """``data-*`` kwargs take precedence over ``RECAPTCHA_DATA_ATTRS`` config."""
    app.config["RECAPTCHA_DATA_ATTRS"] = {"theme": "light"}
    f = RecaptchaForm()
    render = f.recaptcha(data_theme="dark")
    assert 'data-theme="dark"' in render
    assert "light" not in render


def test_render_kwargs_override_id():
    """``id`` kwarg overrides the default field id."""
    f = RecaptchaForm()
    render = f.recaptcha(id="custom-id")
    assert 'id="custom-id"' in render


def test_render_kwargs_are_escaped():
    """HTML attribute values from kwargs are escaped."""
    f = RecaptchaForm()
    render = f.recaptcha(title='"><script>alert(1)</script>')
    assert "<script>alert(1)</script>" not in render
    assert "&lt;script&gt;" in render


def test_missing_response(app):
    with app.test_request_context():
        f = RecaptchaForm()
        f.validate()
        assert f.recaptcha.errors[0] == "The response parameter is missing."


class MockResponse:
    def __init__(self, code, error="invalid-input-response", read_bytes=False):
        self.code = code
        self.data = json.dumps(
            {"success": not error, "error-codes": [error] if error else []}
        )
        self.read_bytes = read_bytes

    def read(self):
        if self.read_bytes:
            return self.data.encode("utf-8")

        return self.data


def test_send_invalid_request(monkeypatch):
    def mock_urlopen(url, data):
        return MockResponse(200)

    monkeypatch.setattr(http, "urlopen", mock_urlopen)
    f = RecaptchaForm()
    f.validate()
    assert f.recaptcha.errors[0] == ("The response parameter is invalid or malformed.")


def test_response_from_json(app, monkeypatch):
    def mock_urlopen(url, data):
        return MockResponse(200)

    monkeypatch.setattr(http, "urlopen", mock_urlopen)

    with app.test_request_context(
        data=json.dumps({"g-recaptcha-response": "pass"}),
        content_type="application/json",
    ):
        f = RecaptchaForm()
        f.validate()
        assert f.recaptcha.errors[0] != "The response parameter is missing."


def test_request_fail(monkeypatch):
    def mock_urlopen(url, data):
        return MockResponse(400)

    monkeypatch.setattr(http, "urlopen", mock_urlopen)
    f = RecaptchaForm()
    f.validate()
    assert f.recaptcha.errors


def test_request_success(monkeypatch):
    def mock_urlopen(url, data):
        return MockResponse(200, "")

    monkeypatch.setattr(http, "urlopen", mock_urlopen)
    f = RecaptchaForm()
    f.validate()
    assert not f.recaptcha.errors


def test_request_custom_verify_server(app, monkeypatch):
    verify_server = "https://hcaptcha.com/siteverify"

    def mock_urlopen(url, data):
        assert url == verify_server
        return MockResponse(200, "")

    monkeypatch.setattr(http, "urlopen", mock_urlopen)
    app.config["RECAPTCHA_VERIFY_SERVER"] = verify_server
    f = RecaptchaForm()
    f.validate()
    assert not f.recaptcha.errors


def test_request_unmatched_error(monkeypatch):
    def mock_urlopen(url, data):
        return MockResponse(200, "not-an-error", True)

    monkeypatch.setattr(http, "urlopen", mock_urlopen)
    f = RecaptchaForm()
    f.recaptcha.validators = [Recaptcha("custom")]
    f.validate()
    assert f.recaptcha.errors[0] == "custom"
