Changes
=======

Version 1.2.2
-------------

Released 2024-10-20

- Move the project to the pallets-eco organization. :pr:`602`
- Stop support for Python 3.8. Start support for Python 3.13. :pr:`603`

Version 1.2.1
-------------

Released 2023-10-02

- Fix a bug introduced with :pr:`556` where file validators were editing
  the file fields content. :pr:`578`

Version 1.2.0
-------------

Released 2023-10-01

-   Add field ``MultipleFileField``. ``FileRequired``, ``FileAllowed``, ``FileSize``
    now can be used to validate multiple files :pr:`556` :issue:`338`

Version 1.1.2
-------------

Released 2023-09-29

-   Fixed Flask 2.3 deprecations of ``werkzeug.urls.url_encode`` and
    ``flask.Markup`` :pr:`565` :issue:`561`
-   Stop support for python 3.7 :pr:`574`
-   Use `pyproject.toml` instead of `setup.cfg` :pr:`576`
-   Fixed nested blueprint CSRF exemption :pr:`572`

Version 1.1.1
-------------

Released 2023-01-17

-   Fixed `validate` `extra_validators` parameter. :pr:`548`

Version 1.1.0
-------------

Released 2023-01-15

-   Drop support for Python 3.6.
-   ``validate_on_submit`` takes a ``extra_validators`` parameters :pr:`479`
-   Stop supporting Flask-Babelex :pr:`540`
-   Support for python 3.11 :pr:`542`
-   Remove unused call to `JSONEncoder` :pr:`536`

Version 1.0.1
-------------

Released 2022-03-31

-   Update compatibility with the latest Werkzeug release. :issue:`511`


Version 1.0.0
--------------

Released 2021-11-07

-   Deprecated items removal :pr:`484`
-   Support for alternatives captcha services :pr:`425` :pr:`342`
    :pr:`387` :issue:`384`

Version 0.15.1
--------------

Released 2021-05-25

-   Add ``python_requires`` metadata to avoid installing on unsupported
    Python versions. :pr:`442`


Version 0.15.0
--------------

Released 2021-05-24

-   Drop support for Python < 3.6. :pr:`416`
-   ``FileSize`` validator. :pr:`307, 365`
-   Extra requirement ``email`` installs the ``email_validator``
    package. :pr:`423`
-   Fixed Flask 2.0 warnings. :pr:`434`
-   Various documentation fixes. :pr:`315, 321, 335, 344, 386, 400`,
    :pr:`404, 420, 437`
-   Various CI fixes. :pr:`405, 438`


Version 0.14.3
--------------

Released 2020-02-06

-   Fix deprecated imports from ``werkzeug`` and ``collections``.


Version 0.14.2
--------------

Released 2017-01-10

-   Fix bug where ``FlaskForm`` assumed ``meta`` argument was not
    ``None`` if it was passed. :issue:`278`


Version 0.14.1
--------------

Released 2017-01-10

-   Fix bug where the file validators would incorrectly identify an
    empty file as valid data. :issue:`276`, :pr:`277`

    -   ``FileField`` is no longer deprecated. The data is checked
        during processing and only set if it's a valid file.
    -   ``has_file`` *is* deprecated; it's now equivalent to
        ``bool(field.data)``.
    -   ``FileRequired`` and ``FileAllowed`` work with both the
        Flask-WTF and WTForms ``FileField`` classes.
    -   The ``Optional`` validator now works with ``FileField``.


Version 0.14
------------

Released 2017-01-06

-   Use ItsDangerous to sign CSRF tokens and check expiration instead of
    doing it ourselves. :issue:`264`

    -   All tokens are URL safe, removing the ``url_safe`` parameter
        from ``generate_csrf``. :issue:`206`
    -   All tokens store a timestamp, which is checked in
        ``validate_csrf``. The ``time_limit`` parameter of
        ``generate_csrf`` is removed.

-   Remove the ``app`` attribute from ``CsrfProtect``, use
    ``current_app``. :issue:`264`
-   ``CsrfProtect`` protects the ``DELETE`` method by default.
    :issue:`264`
-   The same CSRF token is generated for the lifetime of a request. It
    is exposed as ``g.csrf_token`` for use during testing.
    :issue:`227, 264`
-   ``CsrfProtect.error_handler`` is deprecated. :issue:`264`

    -   Handlers that return a response work in addition to those that
        raise an error. The behavior was not clear in previous docs.
    -   :issue:`200, 209, 243, 252`

-   Use ``Form.Meta`` instead of deprecated ``SecureForm`` for CSRF (and
    everything else). :issue:`216, 271`

    -   ``csrf_enabled`` parameter is still recognized but deprecated.
        All other attributes and methods from ``SecureForm`` are
        removed. :issue:`271`

-   Provide ``WTF_CSRF_FIELD_NAME`` to configure the name of the CSRF
    token. :issue:`271`
-   ``validate_csrf`` raises ``wtforms.ValidationError`` with specific
    messages instead of returning ``True`` or ``False``. This breaks
    anything that was calling the method directly. :issue:`239, 271`

    -   CSRF errors are logged as well as raised. :issue:`239`

-   ``CsrfProtect`` is renamed to ``CSRFProtect``. A deprecation warning
    is issued when using the old name. ``CsrfError`` is renamed to
    ``CSRFError`` without deprecation. :issue:`271`
-   ``FileField`` is deprecated because it no longer provides
    functionality over the provided validators. Use
    ``wtforms.FileField`` directly. :issue:`272`


Version 0.13.1
--------------

Released 2016-10-6

-   Deprecation warning for ``Form`` is shown during ``__init__``
    instead of immediately when subclassing. :issue:`262`
-   Don't use ``pkg_resources`` to get version, for compatibility with
    GAE. :issue:`261`


Version 0.13
------------

Released 2016-09-29

-   ``Form`` is renamed to ``FlaskForm`` in order to avoid name
    collision with WTForms's base class.  Using ``Form`` will show a
    deprecation warning. :issue:`250`
-   ``hidden_tag`` no longer wraps the hidden inputs in a hidden div.
    This is valid HTML5 and any modern HTML parser will behave
    correctly. :issue:`193, 217`
-   ``flask_wtf.html5`` is deprecated. Import directly from
    ``wtforms.fields.html5``. :issue:`251`
-   ``is_submitted`` is true for ``PATCH`` and ``DELETE`` in addition to
    ``POST`` and ``PUT``. :issue:`187`
-   ``generate_csrf`` takes a ``token_key`` parameter to specify the key
    stored in the session. :issue:`206`
-   ``generate_csrf`` takes a ``url_safe`` parameter to allow the token
    to be used in URLs. :issue:`206`
-   ``form.data`` can be accessed multiple times without raising an
    exception. :issue:`248`
-   File extension with multiple parts (``.tar.gz``) can be used in the
    ``FileAllowed`` validator. :issue:`201`


Version 0.12
------------

Released 2015-07-09

-   Abstract ``protect_csrf()`` into a separate method.
-   Update reCAPTCHA configuration.
-   Fix reCAPTCHA error handle.


Version 0.11
------------

Released 2015-01-21

-   Use the new reCAPTCHA API. :pr:`164`


Version 0.10.3
--------------

Released 2014-11-16

-   Add configuration: ``WTF_CSRF_HEADERS``. :pr:`159`
-   Support customize hidden tags. :pr:`150`
-   And many more bug fixes.


Version 0.10.2
--------------

Released 2014-09-03

-   Update translation for reCaptcha. :pr:`146`


Version 0.10.1
--------------

Released 2014-08-26

-   Update ``RECAPTCHA_API_SERVER_URL``. :pr:`145`
-   Update requirement Werkzeug >= 0.9.5.
-   Fix ``CsrfProtect`` exempt for blueprints. :pr:`143`


Version 0.10.0
--------------

Released 2014-07-16

-   Add configuration: ``WTF_CSRF_METHODS``.
-   Support WTForms 2.0 now.
-   Fix CSRF validation without time limit (``time_limit=False``).
-   ``csrf_exempt`` supports blueprint. :issue:`111`


Version 0.9.5
-------------

Released 2014-03-21

-   ``csrf_token`` for all template types. :pr:`112`
-   Make ``FileRequired`` a subclass of ``InputRequired``. :pr:`108`


Version 0.9.4
-------------

Released 2013-12-20

-   Bugfix for ``csrf`` module when form has a prefix.
-   Compatible support for WTForms 2.
-   Remove file API for ``FileField``


Version 0.9.3
-------------

Released 2013-10-02

-   Fix validation of recaptcha when app in testing mode. :pr:`89`
-   Bugfix for ``csrf`` module. :pr:`91`


Version 0.9.2
-------------

Released 2013-09-11

-   Upgrade WTForms to 1.0.5.
-   No lazy string for i18n. :issue:`77`
-   No ``DateInput`` widget in HTML5. :issue:`81`
-   ``PUT`` and ``PATCH`` for CSRF. :issue:`86`


Version 0.9.1
-------------

Released 2013-08-21

-   Compatibility with Flask < 0.10. :issue:`82`


Version 0.9.0
-------------

Released 2013-08-15

-   Add i18n support. :issue:`65`
-   Use default HTML5 widgets and fields provided by WTForms.
-   Python 3.3+ support.
-   Redesign form, replace ``SessionSecureForm``.
-   CSRF protection solution.
-   Drop WTForms imports.
-   Fix recaptcha i18n support.
-   Fix recaptcha validator for Python 3.
-   More test cases, it's 90%+ coverage now.
-   Redesign documentation.


Version 0.8.4
-------------

Released 2013-03-28

-   Recaptcha Validator now returns provided message. :issue:`66`
-   Minor doc fixes.
-   Fixed issue with tests barking because of nose/multiprocessing
    issue.


Version 0.8.3
-------------

Released 2013-03-13

-   Update documentation to indicate pending deprecation of WTForms
    namespace facade.
-   PEP8 fixes. :issue:`64`
-   Fix Recaptcha widget. :issue:`49`


Version 0.8.2 and prior
-----------------------

Initial development by Dan Jacob and Ron Duplain.
