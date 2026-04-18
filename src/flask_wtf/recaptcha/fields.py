from wtforms.fields import Field

from . import widgets
from .validators import Recaptcha

__all__ = ["RecaptchaField"]


class RecaptchaField(Field):
    """reCAPTCHA field using :class:`.Recaptcha` as its default validator.

    The default validator skips verification when ``current_app.testing`` is
    ``True``, so tests don't need a real reCAPTCHA token.

    When using a nonce-based Content Security Policy, pass ``nonce`` to
    populate the ``nonce`` attribute of the generated ``<script>`` tag. A
    zero-argument callable is accepted so the value can be resolved at
    render time, e.g. ``nonce=lambda: g.csp_nonce``.
    """

    widget = widgets.RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label="", validators=None, nonce=None, **kwargs):
        validators = validators or [Recaptcha()]
        self.nonce = nonce
        super().__init__(label, validators, **kwargs)
