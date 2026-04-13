"""
订单管理测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestOrders:
    """订单管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers
        # 创建分类和菜品
        cat_resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "订单测试分类",
            "sort_order": 1
        })
        self.cat_id = cat_resp.json()["id"]

        dish_resp = requests.post(f"{BASE_URL}/api/dishes", headers=self.headers, json={
            "category_id": self.cat_id,
            "name": "订单测试菜品",
            "price": 30.00,
            "status": "active"
        })
        self.dish_id = dish_resp.json()["id"]

        # 创建桌位
        table_resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T_ORDER",
            "name": "订单测试桌",
            "status": "idle"
        })
        self.table_id = table_resp.json()["id"]

    def test_list_orders(self):
        """获取订单列表"""
        resp = requests.get(f"{BASE_URL}/api/orders", headers=self.headers)
        assert resp.status_code == 200

    def test_create_order(self):
        """创建订单"""
        resp = requests.post(f"{BASE_URL}/api/orders", headers=self.headers, json={
            "table_id": self.table_id,
            "items": [{
                "dish_id": self.dish_id,
                "dish_name": "测试菜品",
                "price": 30.00,
                "quantity": 2
            }],
            "total_amount": 60.00,
            "status": "pending"
        })
        assert resp.status_code == 200
        assert resp.json()["total_amount"] == 60.00
        return resp.json()["id"]

    def test_update_order_status(self):
        """更新订单状态"""
        # 先创建订单
        create_resp = requests.post(f"{BASE_URL}/api/orders", headers=self.headers, json={
            "table_id": self.table_id,
            "items": [{
                "dish_id": self.dish_id,
                "dish_name": "测试菜品",
                "price": 30.00,
                "quantity": 1
            }],
            "total_amount": 30.00,
            "status": "pending"
        })
        order_id = create_resp.json()["id"]

        # 更新为已支付
        resp = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", headers=self.headers, json={
            "status": "paid"
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "paid"

    def test_cancel_order(self):
        """取消订单"""
        create_resp = requests.post(f"{BASE_URL}/api/orders", headers=self.headers, json={
            "table_id": self.table_id,
            "items": [{
                "dish_id": self.dish_id,
                "dish_name": "测试菜品",
                "price": 30.00,
                "quantity": 1
            }],
            "total_amount": 30.00,
            "status": "pending"
        })
        order_id = create_resp.json()["id"]

        resp = requests.delete(f"{BASE_URL}/api/orders/{order_id}", headers=self.headers)
        assert resp.status_code == 200
