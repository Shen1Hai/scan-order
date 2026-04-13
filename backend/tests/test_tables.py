"""
桌位管理测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestTables:
    """桌位管理测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers

    def test_list_tables(self):
        """获取桌位列表"""
        resp = requests.get(f"{BASE_URL}/api/tables", headers=self.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_table(self):
        """创建桌位"""
        resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T99",
            "name": "测试桌",
            "status": "idle"
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "测试桌"
        return resp.json()["id"]

    def test_update_table(self):
        """更新桌位"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T100",
            "name": "原桌",
            "status": "idle"
        })
        table_id = create_resp.json()["id"]

        # 更新
        resp = requests.put(f"{BASE_URL}/api/tables/{table_id}", headers=self.headers, json={
            "status": "occupied"
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "occupied"

    def test_table_qrcode(self):
        """生成桌位二维码"""
        # 先创建
        create_resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T101",
            "name": "二维码测试桌",
            "status": "idle"
        })
        table_id = create_resp.json()["id"]

        # 获取二维码
        resp = requests.get(f"{BASE_URL}/api/tables/{table_id}/qrcode", headers=self.headers)
        assert resp.status_code == 200

    def test_delete_table(self):
        """删除桌位"""
        create_resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T102",
            "name": "待删除桌",
            "status": "idle"
        })
        table_id = create_resp.json()["id"]

        resp = requests.delete(f"{BASE_URL}/api/tables/{table_id}", headers=self.headers)
        assert resp.status_code == 200
