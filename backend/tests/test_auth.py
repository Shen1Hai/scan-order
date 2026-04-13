"""
认证测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestAuth:
    """认证相关测试"""

    def test_login_success(self):
        """登录成功"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """密码错误"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "wrong"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        """用户不存在"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "nonexistent",
            "password": "admin123"
        })
        assert resp.status_code == 401

    def test_profile(self, headers):
        """获取用户信息"""
        resp = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["role"] == "super_admin"

    def test_permissions(self, headers):
        """获取权限列表"""
        resp = requests.get(f"{BASE_URL}/api/auth/permissions", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "permissions" in data
        assert len(data["permissions"]) > 0

    def test_merchants(self, headers):
        """获取商户列表"""
        resp = requests.get(f"{BASE_URL}/api/auth/merchants", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "merchants" in data
        assert len(data["merchants"]) > 0
