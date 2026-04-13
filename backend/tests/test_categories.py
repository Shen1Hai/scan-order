"""
分类管理测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestCategories:
    """分类管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers

    def test_list_categories(self):
        """获取分类列表"""
        resp = requests.get(f"{BASE_URL}/api/categories", headers=self.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_category(self):
        """创建分类"""
        resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "测试分类",
            "sort_order": 10
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "测试分类"
        return data["id"]

    def test_update_category(self):
        """更新分类"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "原名称",
            "sort_order": 1
        })
        cat_id = create_resp.json()["id"]

        # 再更新
        resp = requests.put(f"{BASE_URL}/api/categories/{cat_id}", headers=self.headers, json={
            "name": "新名称"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "新名称"

    def test_delete_category(self):
        """删除分类"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "待删除分类",
            "sort_order": 1
        })
        cat_id = create_resp.json()["id"]

        # 删除
        resp = requests.delete(f"{BASE_URL}/api/categories/{cat_id}", headers=self.headers)
        assert resp.status_code == 200
