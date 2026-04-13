"""
报表统计测试
"""
import pytest
import requests

BASE_URL = "http://localhost:8000"

class TestReports:
    """报表统计测试"""

    @pytest.fixture(autouse=True)
    def setup(self, headers):
        self.headers = headers

    def test_dashboard(self):
        """仪表盘"""
        resp = requests.get(f"{BASE_URL}/api/reports/dashboard", headers=self.headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "today_sales" in data
        assert "today_orders" in data

    def test_sales_report(self):
        """销售报表"""
        resp = requests.get(f"{BASE_URL}/api/reports/sales", headers=self.headers)
        assert resp.status_code == 200

    def test_dishes_report(self):
        """菜品报表"""
        resp = requests.get(f"{BASE_URL}/api/reports/dishes", headers=self.headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_staff_report(self):
        """员工业绩报表"""
        resp = requests.get(f"{BASE_URL}/api/reports/staff", headers=self.headers)
        assert resp.status_code == 200
