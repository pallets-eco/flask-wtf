from urllib.parse import urlencode

from flask import current_app
from markupsafe import escape
from markupsafe import Markup
from wtforms.widgets import html_params

RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"

__all__ = ["RecaptchaWidget"]


class RecaptchaWidget:
    def recaptcha_html(self, public_key, nonce=None, **kwargs):
        html = current_app.config.get("RECAPTCHA_HTML")
        if html:
            return Markup(html)
        params = current_app.config.get("RECAPTCHA_PARAMETERS")
        script = current_app.config.get("RECAPTCHA_SCRIPT")
        if not script:
            script = RECAPTCHA_SCRIPT_DEFAULT
        if params:
            script += f"?{urlencode(params)}"
        if callable(nonce):
            nonce = nonce()
        nonce_attr = f' nonce="{escape(nonce)}"' if nonce else ""

        kwargs.setdefault(
            "class",
            current_app.config.get("RECAPTCHA_DIV_CLASS")
            or RECAPTCHA_DIV_CLASS_DEFAULT,
        )

        data_attrs = dict(current_app.config.get("RECAPTCHA_DATA_ATTRS", {}))
        data_attrs["sitekey"] = public_key
        for k, v in data_attrs.items():
            kwargs.setdefault(f"data-{k}", v)

        attributes = html_params(**kwargs)
        return Markup(
            f"\n<script src='{script}' async defer{nonce_attr}></script>\n"
            f"<div {attributes}></div>\n"
        )

    def __call__(self, field, error=None, **kwargs):
        """Returns the recaptcha input HTML."""

        if not current_app.config.get("RECAPTCHA_ENABLED", True):
            return Markup("<!-- recaptcha disabled -->")

        try:
            public_key = current_app.config["RECAPTCHA_PUBLIC_KEY"]
        except KeyError:
            raise RuntimeError("RECAPTCHA_PUBLIC_KEY config not set") from None

        kwargs.setdefault("id", field.id)
        return self.recaptcha_html(public_key, nonce=field.nonce, **kwargs)
