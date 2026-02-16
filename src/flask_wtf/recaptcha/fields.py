from wtforms.fields import Field

from . import widgets
from .validators import Recaptcha

__all__ = ["RecaptchaField"]


class RecaptchaField(Field):
    """The field will always be valid if current_app.testing is True"""

    widget = widgets.RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error = None

    def __init__(self, label="", validators=None, **kwargs):
        validators = validators or [Recaptcha()]
        super().__init__(label, validators, **kwargs)
