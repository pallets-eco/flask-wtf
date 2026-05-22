import pytest
from flask import request
from wtforms import EmailField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length

from flask_wtf import FlaskForm

pytest.importorskip("flask_wtf.i18n", reason="Flask-Babel is not installed.")


class NameForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField(validators=[DataRequired(), Length(min=8)])


def test_no_extension(app, client):
    @app.route("/", methods=["POST"])
    def index():
        form = NameForm()
        form.validate()
        assert form.name.errors[0] == "This field is required."

    client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})


def test_i18n(app, client):
    try:
        from flask_babel import Babel
    except ImportError:
        pytest.skip("Flask-Babel must be installed.")

    def get_locale():
        return request.accept_languages.best_match(["en", "zh"], "en")

    Babel(app, locale_selector=get_locale)

    @app.route("/", methods=["POST"])
    def index():
        form = NameForm()
        form.validate()

        if not app.config.get("WTF_I18N_ENABLED", True):
            assert form.name.errors[0] == "This field is required."
        elif not form.name.data:
            assert form.name.errors[0] == "该字段是必填字段。"
        else:
            assert form.name.errors[0] == "字段长度必须至少 8 个字符。"

    client.post("/", headers={"Accept-Language": "zh-CN,zh;q=0.8"})
    client.post("/", headers={"Accept-Language": "zh"}, data={"name": "short"})
    app.config["WTF_I18N_ENABLED"] = False
    client.post("/", headers={"Accept-Language": "zh"})


def test_outside_request():
    pytest.importorskip("babel")
    from flask_wtf.i18n import translations

    s = "This field is required."
    assert translations.gettext(s) == s

    ss = "Field must be at least %(min)d character long."
    sp = "Field must be at least %(min)d character long."
    assert translations.ngettext(ss, sp, 1) == ss
    assert translations.ngettext(ss, sp, 2) == sp


def test_meta_locales_respected_without_babel_extension(app, client):
    """Without Babel(app) initialised, FlaskForm should fall back to
    WTForms-level translations and honour ``meta={'locales': [...]}``,
    matching vanilla wtforms behaviour. See #582.
    """

    class EmailForm(FlaskForm):
        class Meta:
            csrf = False

        email = EmailField(validators=[Email()])

    @app.route("/", methods=["POST"])
    def index():
        form = EmailForm(meta={"locales": ["fr"]})
        form.validate()
        return form.errors

    res = client.post("/", data={"email": "invalid-email"})
    # Without Babel(app) initialised, the meta locales should still be
    # honoured by the underlying WTForms translation machinery.
    assert "Invalid email address." not in res.json["email"]
    assert "Adresse électronique non valide." in res.json["email"]
