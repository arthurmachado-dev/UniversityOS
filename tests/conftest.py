import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402


@pytest.fixture()
def data_dir(tmp_path):
    return tmp_path / "data"


@pytest.fixture()
def app(data_dir):
    return create_app(data_dir=data_dir, testing=True)


@pytest.fixture()
def client(app):
    return app.test_client()
