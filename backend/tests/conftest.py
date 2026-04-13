"""
pytest 配置
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def token():
    """登录获取token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert resp.status_code == 200, f"登录失败: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture(scope="session")
def headers(token):
    """请求头"""
    return {"Authorization": f"Bearer {token}"}
