import os
from collections import abc

from werkzeug.datastructures import FileStorage
from wtforms import FileField as _FileField
from wtforms import MultipleFileField as _MultipleFileField
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation
from wtforms.validators import ValidationError


class FileField(_FileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.FileField`."""

    def process_formdata(self, valuelist):
        valid_files = (
            file for file in valuelist if file and isinstance(file, FileStorage)
        )
        data = next(valid_files, None)

        if data is not None:
            self.data = data
        else:
            self.raw_data = []


class MultipleFileField(_MultipleFileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.MultipleFileField`.

    .. versionadded:: 1.2.0
    """

    def process_formdata(self, valuelist):
        valid_files = [
            file for file in valuelist if file and isinstance(file, FileStorage)
        ]

        if valid_files:
            self.data = valid_files
        else:
            self.raw_data = []


class FileRequired(DataRequired):
    """Validates that the uploaded files(s) is a Werkzeug
    :class:`~werkzeug.datastructures.FileStorage` object.

    :param message: error message

    You can also use the synonym ``file_required``.
    """

    def __call__(self, form, field):
        field_data = [field.data] if not isinstance(field.data, list) else field.data
        if not (
            field_data
            and all((file and isinstance(file, FileStorage)) for file in field_data)
        ):
            raise StopValidation(
                self.message or field.gettext("This field is required.")
            )


file_required = FileRequired


class FileAllowed:
    """Validates that the uploaded file(s) is allowed by a given list of
    extensions or a Flask-Uploads :class:`~flaskext.uploads.UploadSet`.

    :param upload_set: A list of extensions or an
        :class:`~flaskext.uploads.UploadSet`
    :param message: error message

    You can also use the synonym ``file_allowed``.
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        field_data = field.data if isinstance(field.data, list) else [field.data]
        if not (
            field_data
            and all(file and isinstance(file, FileStorage) for file in field_data)
        ):
            return

        filenames = [f.filename.lower() for f in field_data]

        for filename in filenames:
            if isinstance(self.upload_set, abc.Iterable):
                if any(filename.endswith(f".{x}") for x in self.upload_set):
                    continue

                raise StopValidation(
                    self.message
                    or field.gettext(
                        "File does not have an approved extension: {extensions}"
                    ).format(extensions=", ".join(self.upload_set))
                )

            if not self.upload_set.file_allowed(field_data, filename):
                raise StopValidation(
                    self.message
                    or field.gettext("File does not have an approved extension.")
                )


file_allowed = FileAllowed


class FileSize:
    """Validates that the uploaded file(s) is within a minimum and maximum
    file size (set in bytes).

    :param min_size: minimum allowed file size (in bytes). Defaults to 0 bytes.
    :param max_size: maximum allowed file size (in bytes).
    :param message: error message

    You can also use the synonym ``file_size``.
    """

    def __init__(self, max_size, min_size=0, message=None):
        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field):
        field_data = field.data if isinstance(field.data, list) else [field.data]
        if not (
            field_data
            and all(file and isinstance(file, FileStorage) for file in field_data)
        ):
            return

        for f in field_data:
            initial_pos = f.stream.tell()
            f.stream.seek(0, os.SEEK_END)
            file_size = f.stream.tell()
            f.stream.seek(initial_pos)

            if (file_size < self.min_size) or (file_size > self.max_size):
                # the file is too small or too big => validation failure
                raise ValidationError(
                    self.message
                    or field.gettext(
                        f"File must be between {self.min_size}"
                        f" and {self.max_size} bytes."
                    )
                )


file_size = FileSize
