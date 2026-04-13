"""
员工管理测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestStaff:
    """员工管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers

    def test_list_staff(self):
        """获取员工列表"""
        resp = requests.get(f"{BASE_URL}/api/staff", headers=self.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_staff(self):
        """创建员工"""
        resp = requests.post(f"{BASE_URL}/api/staff", headers=self.headers, json={
            "username": "testuser",
            "name": "测试员工",
            "password": "test123",
            "role_id": 2
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "测试员工"

    def test_update_staff(self):
        """更新员工"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/staff", headers=self.headers, json={
            "username": "testuser2",
            "name": "原名称",
            "password": "test123",
            "role_id": 2
        })
        staff_id = create_resp.json()["id"]

        # 更新
        resp = requests.put(f"{BASE_URL}/api/staff/{staff_id}", headers=self.headers, json={
            "name": "新名称"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_delete_staff(self):
        """删除员工"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/staff", headers=self.headers, json={
            "username": "testuser3",
            "name": "待删除员工",
            "password": "test123",
            "role_id": 2
        })
        staff_id = create_resp.json()["id"]

        # 删除
        resp = requests.delete(f"{BASE_URL}/api/staff/{staff_id}", headers=self.headers)
        assert resp.status_code == 200
