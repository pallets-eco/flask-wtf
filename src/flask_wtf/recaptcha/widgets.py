from urllib.parse import urlencode

from flask import current_app
from markupsafe import Markup

RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"
RECAPTCHA_NONCE = ' nonce="%s"'
RECAPTCHA_TEMPLATE = """
<script src='%s' async defer%s></script>
<div class="%s" %s></div>
"""

__all__ = ["RecaptchaWidget"]


class RecaptchaWidget:
    def recaptcha_html(self, public_key, nonce=None):
        html = current_app.config.get("RECAPTCHA_HTML")
        if html:
            return Markup(html)
        params = current_app.config.get("RECAPTCHA_PARAMETERS")
        script = current_app.config.get("RECAPTCHA_SCRIPT")
        if not script:
            script = RECAPTCHA_SCRIPT_DEFAULT
        if params:
            script += "?" + urlencode(params)
        nonce_attr = ""
        if nonce is not None:
            nonce_attr = RECAPTCHA_NONCE % nonce
        attrs = current_app.config.get("RECAPTCHA_DATA_ATTRS", {})
        attrs["sitekey"] = public_key
        snippet = " ".join(f'data-{k}="{attrs[k]}"' for k in attrs)  # noqa: B028, B907
        div_class = current_app.config.get("RECAPTCHA_DIV_CLASS")
        if not div_class:
            div_class = RECAPTCHA_DIV_CLASS_DEFAULT
        return Markup(RECAPTCHA_TEMPLATE % (script, nonce_attr, div_class, snippet))

    def __call__(self, field, error=None, **kwargs):
        """Returns the recaptcha input HTML."""

        try:
            public_key = current_app.config["RECAPTCHA_PUBLIC_KEY"]
        except KeyError:
            raise RuntimeError("RECAPTCHA_PUBLIC_KEY config not set") from None

        return self.recaptcha_html(public_key, nonce=field.nonce)
