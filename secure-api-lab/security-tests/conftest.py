import os

import httpx
import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10) as c:
        yield c

