from urllib.parse import urlencode

from flask import current_app
from markupsafe import escape
from markupsafe import Markup

RECAPTCHA_SCRIPT_DEFAULT = "https://www.google.com/recaptcha/api.js"
RECAPTCHA_DIV_CLASS_DEFAULT = "g-recaptcha"
RECAPTCHA_TEMPLATE = """
<script src='{script}' async defer{nonce_attr}></script>
<div class="{div_class}" {snippet}></div>
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
            script += f"?{urlencode(params)}"
        if callable(nonce):
            nonce = nonce()
        nonce_attr = f' nonce="{escape(nonce)}"' if nonce else ""
        attrs = current_app.config.get("RECAPTCHA_DATA_ATTRS", {})
        attrs["sitekey"] = public_key
        snippet = " ".join(f'data-{k}="{attrs[k]}"' for k in attrs)  # noqa: B028, B907
        div_class = current_app.config.get("RECAPTCHA_DIV_CLASS")
        if not div_class:
            div_class = RECAPTCHA_DIV_CLASS_DEFAULT
        return Markup(
            RECAPTCHA_TEMPLATE.format(
                script=script,
                nonce_attr=nonce_attr,
                div_class=div_class,
                snippet=snippet,
            )
        )

    def __call__(self, field, error=None, **kwargs):
        """Returns the recaptcha input HTML."""

        try:
            public_key = current_app.config["RECAPTCHA_PUBLIC_KEY"]
        except KeyError:
            raise RuntimeError("RECAPTCHA_PUBLIC_KEY config not set") from None

        return self.recaptcha_html(public_key, nonce=field.nonce)
