"""
库存管理测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestInventory:
    """库存管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers

    def test_list_inventory(self):
        """获取库存列表"""
        resp = requests.get(f"{BASE_URL}/api/inventory", headers=self.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_inventory(self):
        """创建库存"""
        resp = requests.post(f"{BASE_URL}/api/inventory", headers=self.headers, json={
            "name": "测试食材",
            "quantity": 100.0,
            "unit": "kg",
            "low_stock_threshold": 20.0
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "测试食材"
        return resp.json()["id"]

    def test_update_inventory(self):
        """更新库存"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/inventory", headers=self.headers, json={
            "name": "原食材",
            "quantity": 50.0,
            "unit": "kg"
        })
        inv_id = create_resp.json()["id"]

        # 更新
        resp = requests.put(f"{BASE_URL}/api/inventory/{inv_id}", headers=self.headers, json={
            "quantity": 80.0
        })
        assert resp.status_code == 200

    def test_inventory_log(self):
        """库存出入库记录"""
        # 先创建库存
        create_resp = requests.post(f"{BASE_URL}/api/inventory", headers=self.headers, json={
            "name": "记录测试食材",
            "quantity": 100.0,
            "unit": "kg"
        })
        inv_id = create_resp.json()["id"]

        # 入库
        resp = requests.post(f"{BASE_URL}/api/inventory/{inv_id}/log", headers=self.headers, json={
            "type": "in",
            "quantity": 50.0,
            "note": "测试入库"
        })
        assert resp.status_code == 200

        # 出库
        resp = requests.post(f"{BASE_URL}/api/inventory/{inv_id}/log", headers=self.headers, json={
            "type": "out",
            "quantity": 20.0,
            "note": "测试出库"
        })
        assert resp.status_code == 200

    def test_delete_inventory(self):
        """删除库存"""
        create_resp = requests.post(f"{BASE_URL}/api/inventory", headers=self.headers, json={
            "name": "待删除食材",
            "quantity": 50.0,
            "unit": "kg"
        })
        inv_id = create_resp.json()["id"]

        resp = requests.delete(f"{BASE_URL}/api/inventory/{inv_id}", headers=self.headers)
        assert resp.status_code == 200
