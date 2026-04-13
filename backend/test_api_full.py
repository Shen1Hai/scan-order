"""
全面 API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.results = []

    def log(self, name, status, detail=""):
        symbol = "✓" if status else "✗"
        msg = f"[{symbol}] {name}"
        if detail:
            msg += f" - {detail}"
        print(msg)
        self.results.append((name, status))

    def login(self):
        """登录"""
        print("\n=== 登录测试 ===")
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        self.log("登录 admin/admin123", resp.status_code == 200, resp.text[:50] if resp.status_code != 200 else "OK")
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            return True
        return False

    def test_categories(self):
        """分类管理"""
        print("\n=== 分类管理 ===")
        # 获取分类
        resp = requests.get(f"{BASE_URL}/api/categories", headers=self.headers)
        self.log("获取分类列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 创建分类
        resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "热菜",
            "sort_order": 1
        })
        self.log("创建分类-热菜", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])
        cat_id = resp.json().get("id") if resp.status_code == 200 else None

        resp = requests.post(f"{BASE_URL}/api/categories", headers=self.headers, json={
            "name": "凉菜",
            "sort_order": 2
        })
        self.log("创建分类-凉菜", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])

        # 更新分类
        if cat_id:
            resp = requests.put(f"{BASE_URL}/api/categories/{cat_id}", headers=self.headers, json={
                "name": "热菜-已修改"
            })
            self.log("更新分类", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])

        return cat_id

    def test_dishes(self, cat_id):
        """菜品管理"""
        print("\n=== 菜品管理 ===")
        # 获取菜品
        resp = requests.get(f"{BASE_URL}/api/dishes", headers=self.headers)
        self.log("获取菜品列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 创建菜品
        resp = requests.post(f"{BASE_URL}/api/dishes", headers=self.headers, json={
            "category_id": cat_id,
            "name": "红烧肉",
            "price": 38.00,
            "description": "美味红烧肉",
            "status": "active"
        })
        self.log("创建菜品-红烧肉", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])
        dish_id = resp.json().get("id") if resp.status_code == 200 else None

        resp = requests.post(f"{BASE_URL}/api/dishes", headers=self.headers, json={
            "category_id": cat_id,
            "name": "宫保鸡丁",
            "price": 28.00,
            "status": "active"
        })
        self.log("创建菜品-宫保鸡丁", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])

        # 更新菜品
        if dish_id:
            resp = requests.put(f"{BASE_URL}/api/dishes/{dish_id}", headers=self.headers, json={
                "price": 40.00
            })
            self.log("更新菜品价格", resp.status_code == 200, f"新价格: {resp.json().get('price')}" if resp.status_code == 200 else resp.text[:50])

        return dish_id

    def test_tables(self):
        """桌位管理"""
        print("\n=== 桌位管理 ===")
        # 获取桌位
        resp = requests.get(f"{BASE_URL}/api/tables", headers=self.headers)
        self.log("获取桌位列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 创建桌位
        resp = requests.post(f"{BASE_URL}/api/tables", headers=self.headers, json={
            "code": "T01",
            "name": "1号桌",
            "status": "idle"
        })
        self.log("创建桌位-1号桌", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])
        table_id = resp.json().get("id") if resp.status_code == 200 else None

        # 获取桌位二维码
        if table_id:
            resp = requests.get(f"{BASE_URL}/api/tables/{table_id}/qrcode", headers=self.headers)
            self.log("生成桌位二维码", resp.status_code == 200, "有数据" if resp.status_code == 200 else resp.text[:50])

        # 更新桌位状态
        if table_id:
            resp = requests.put(f"{BASE_URL}/api/tables/{table_id}", headers=self.headers, json={
                "status": "occupied"
            })
            self.log("更新桌位状态", resp.status_code == 200, resp.json().get("status", "") if resp.status_code == 200 else resp.text[:50])

        return table_id

    def test_orders(self, table_id, dish_id):
        """订单管理"""
        print("\n=== 订单管理 ===")
        # 获取订单
        resp = requests.get(f"{BASE_URL}/api/orders", headers=self.headers)
        self.log("获取订单列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 创建订单
        resp = requests.post(f"{BASE_URL}/api/orders", headers=self.headers, json={
            "table_id": table_id,
            "items": [
                {"dish_id": dish_id, "quantity": 2, "price": 40.00, "dish_name": "红烧肉"}
            ],
            "total_amount": 80.00,
            "status": "pending"
        })
        self.log("创建订单", resp.status_code == 200, resp.json().get("order_no", "") if resp.status_code == 200 else resp.text[:50])
        order_id = resp.json().get("id") if resp.status_code == 200 else None

        # 更新订单状态
        if order_id:
            resp = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", headers=self.headers, json={
                "status": "paid"
            })
            self.log("订单支付", resp.status_code == 200, resp.json().get("status", "") if resp.status_code == 200 else resp.text[:50])

            resp = requests.put(f"{BASE_URL}/api/orders/{order_id}/status", headers=self.headers, json={
                "status": "preparing"
            })
            self.log("开始制作", resp.status_code == 200, resp.json().get("status", "") if resp.status_code == 200 else resp.text[:50])

        return order_id

    def test_staff(self):
        """员工管理"""
        print("\n=== 员工管理 ===")
        # 获取员工
        resp = requests.get(f"{BASE_URL}/api/staff", headers=self.headers)
        self.log("获取员工列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 获取角色列表 (从权限接口)
        resp = requests.get(f"{BASE_URL}/api/auth/permissions", headers=self.headers)
        self.log("获取权限列表", resp.status_code == 200, f"数量: {len(resp.json().get('permissions', []))}")

    def test_inventory(self):
        """库存管理"""
        print("\n=== 库存管理 ===")
        # 获取库存
        resp = requests.get(f"{BASE_URL}/api/inventory", headers=self.headers)
        self.log("获取库存列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        # 创建库存
        resp = requests.post(f"{BASE_URL}/api/inventory", headers=self.headers, json={
            "name": "猪肉",
            "quantity": 100.0,
            "unit": "kg",
            "low_stock_threshold": 20.0
        })
        self.log("创建库存-猪肉", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])
        inv_id = resp.json().get("id") if resp.status_code == 200 else None

        # 出入库记录
        if inv_id:
            resp = requests.post(f"{BASE_URL}/api/inventory/{inv_id}/log", headers=self.headers, json={
                "type": "in",
                "quantity": 50.0,
                "note": "进货"
            })
            self.log("库存入库", resp.status_code == 200, "OK" if resp.status_code == 200 else resp.text[:50])

            resp = requests.post(f"{BASE_URL}/api/inventory/{inv_id}/log", headers=self.headers, json={
                "type": "out",
                "quantity": 10.0,
                "note": "使用"
            })
            self.log("库存出库", resp.status_code == 200, "OK" if resp.status_code == 200 else resp.text[:50])

    def test_reports(self):
        """报表"""
        print("\n=== 报表统计 ===")
        resp = requests.get(f"{BASE_URL}/api/reports/dashboard", headers=self.headers)
        self.log("仪表盘数据", resp.status_code == 200, f"今日订单: {resp.json().get('today_orders', 0)}" if resp.status_code == 200 else resp.text[:50])

        resp = requests.get(f"{BASE_URL}/api/reports/sales", headers=self.headers)
        self.log("销售报表", resp.status_code == 200, resp.json() if resp.status_code == 200 else resp.text[:50])

        resp = requests.get(f"{BASE_URL}/api/reports/dishes", headers=self.headers)
        self.log("菜品报表", resp.status_code == 200, f"数量: {len(resp.json())}" if resp.status_code == 200 else resp.text[:50])

    def test_upload(self):
        """文件上传"""
        print("\n=== 文件上传 ===")
        # 创建测试图片
        import io
        from PIL import Image

        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        files = {'file': ('test.png', img_bytes, 'image/png')}
        resp = requests.post(f"{BASE_URL}/api/upload", headers=self.headers, files=files)
        self.log("图片上传", resp.status_code == 200, resp.json().get("url", "") if resp.status_code == 200 else resp.text[:50])

    def test_packages(self):
        """套餐管理"""
        print("\n=== 套餐管理 ===")
        resp = requests.get(f"{BASE_URL}/api/packages", headers=self.headers)
        self.log("获取套餐列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        resp = requests.post(f"{BASE_URL}/api/packages", headers=self.headers, json={
            "name": "双人套餐",
            "price": 88.00,
            "description": "适合2人食用",
            "status": "active"
        })
        self.log("创建套餐-双人套餐", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])

    def test_coupons(self):
        """优惠券管理"""
        print("\n=== 优惠券管理 ===")
        resp = requests.get(f"{BASE_URL}/api/coupons", headers=self.headers)
        self.log("获取优惠券列表", resp.status_code == 200, f"数量: {len(resp.json())}")

        resp = requests.post(f"{BASE_URL}/api/coupons", headers=self.headers, json={
            "name": "新人券",
            "type": "cash",
            "value": 10.00,
            "min_amount": 50.00,
            "status": "active"
        })
        self.log("创建优惠券-新人券", resp.status_code == 200, resp.json().get("name", "") if resp.status_code == 200 else resp.text[:50])

    def run_all(self):
        """运行所有测试"""
        print("=" * 50)
        print("扫码点单系统 - 全面API测试")
        print("=" * 50)

        if not self.login():
            print("登录失败，无法继续测试")
            return

        cat_id = self.test_categories()
        dish_id = self.test_dishes(cat_id)
        table_id = self.test_tables()
        self.test_orders(table_id, dish_id)
        self.test_staff()
        self.test_inventory()
        self.test_reports()
        self.test_upload()
        self.test_packages()
        self.test_coupons()

        # 总结
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        passed = sum(1 for _, s in self.results if s)
        total = len(self.results)
        print(f"通过: {passed}/{total}")
        for name, status in self.results:
            if not status:
                print(f"  失败: {name}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all()
