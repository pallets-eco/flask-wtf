from __future__ import annotations

import typing as t

from wtforms.fields import Field

from . import widgets
from .validators import Recaptcha

__all__ = ["RecaptchaField"]


class RecaptchaField(Field):
    widget = widgets.RecaptchaWidget()

    # error message if recaptcha validation fails
    recaptcha_error: str | None = None

    def __init__(
        self, label: str = "", validators: list[t.Any] | None = None, **kwargs: t.Any
    ) -> None:
        validators = validators or [Recaptcha()]
        super().__init__(label, validators, **kwargs)
