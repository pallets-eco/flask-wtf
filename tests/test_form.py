from io import BytesIO

from flask import json
from flask import request
from wtforms import FileField
from wtforms import HiddenField
from wtforms import IntegerField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.widgets import HiddenInput

from flask_wtf import FlaskForm


class BasicForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField(validators=[DataRequired()])
    avatar = FileField()


def test_populate_from_form(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm()
        assert form.name.data == "form"

    client.post("/", data={"name": "form"})


def test_populate_from_files(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm()
        assert form.avatar.data is not None
        assert form.avatar.data.filename == "flask.png"

    client.post("/", data={"name": "files", "avatar": (BytesIO(), "flask.png")})


def test_populate_from_json(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm()
        assert form.name.data == "json"

    client.post("/", data=json.dumps({"name": "json"}), content_type="application/json")


def test_populate_manually(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm(request.args)
        assert form.name.data == "args"

    client.post("/", query_string={"name": "args"})


def test_populate_none(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm(None)
        assert form.name.data is None

    client.post("/", data={"name": "ignore"})


def test_validate_on_submit(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = BasicForm()
        assert form.is_submitted()
        assert not form.validate_on_submit()
        assert "name" in form.errors

    client.post("/")


def test_no_validate_on_get(app, client):
    @app.route("/", methods=["GET", "POST"])
    def index():
        form = BasicForm()
        assert not form.validate_on_submit()
        assert "name" not in form.errors

    client.get("/")


def test_hidden_tag(req_ctx):
    class F(BasicForm):
        class Meta:
            csrf = True

        key = HiddenField()
        count = IntegerField(widget=HiddenInput())

    f = F()
    out = f.hidden_tag()
    assert all(x in out for x in ("csrf_token", "count", "key"))
    assert "avatar" not in out
    assert "csrf_token" not in f.hidden_tag("count", "key")


def test_set_default_message_language(app, client):
    @app.route("/default", methods=["POST"])
    def default():
        form = BasicForm()
        assert not form.validate_on_submit()
        assert "This field is required." in form.name.errors

    @app.route("/es", methods=["POST"])
    def es():
        app.config["WTF_I18N_ENABLED"] = False

        class MyBaseForm(FlaskForm):
            class Meta:
                csrf = False
                locales = ["es"]

        class NameForm(MyBaseForm):
            name = StringField(validators=[DataRequired()])

        form = NameForm()
        assert form.meta.locales == ["es"]
        assert not form.validate_on_submit()
        assert "Este campo es obligatorio." in form.name.errors

    client.post("/default", data={"name": "  "})
    client.post("/es", data={"name": "  "})


def test_i18n_falls_back_without_babel(app, client, monkeypatch):
    # Regression test: with WTF_I18N_ENABLED left at its default (True) but
    # flask-babel not installed, get_translations() used to unconditionally
    # return `translations`, which is None in that case -- silently
    # discarding the form's own `meta.locales`-based translations instead of
    # falling back to WTForms' own gettext machinery. See flask-wtf#582.
    import flask_wtf.form

    monkeypatch.setattr(flask_wtf.form, "translations", None)

    @app.route("/", methods=["POST"])
    def index():
        class MyBaseForm(FlaskForm):
            class Meta:
                csrf = False
                locales = ["es"]

        class NameForm(MyBaseForm):
            name = StringField(validators=[DataRequired()])

        form = NameForm()
        assert app.config.get("WTF_I18N_ENABLED", True)
        assert not form.validate_on_submit()
        assert "Este campo es obligatorio." in form.name.errors

    client.post("/", data={"name": "  "})
