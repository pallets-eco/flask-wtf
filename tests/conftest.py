from __future__ import annotations

import collections.abc as cabc

import pytest
from flask import Flask as _Flask
from flask.ctx import AppContext
from flask.ctx import RequestContext
from flask.testing import FlaskClient


class Flask(_Flask):
    testing = True
    secret_key = __name__

    def make_response(self, rv):
        if rv is None:
            rv = ""

        return super().make_response(rv)


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    return app


@pytest.fixture
def app_ctx(app: Flask) -> cabc.Generator[AppContext, None, None]:
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture
def req_ctx(app: Flask) -> cabc.Generator[RequestContext, None, None]:
    with app.test_request_context() as ctx:
        yield ctx


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
