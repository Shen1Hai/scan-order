"""
API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """登录获取token"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    print(f"Login: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]

def test_api(token):
    headers = {"Authorization": f"Bearer {token}"}

    # 测试员工列表
    resp = requests.get(f"{BASE_URL}/api/staff", headers=headers)
    print(f"\nGET /api/staff: {resp.status_code}")
    print(resp.json())

    # 创建员工
    resp = requests.post(f"{BASE_URL}/api/staff", headers=headers, json={
        "username": "testadmin",
        "name": "测试用户",
        "password": "testadmin",
        "role_id": 2
    })
    print(f"\nPOST /api/staff: {resp.status_code}")
    print(resp.text)

    # 测试分类
    resp = requests.get(f"{BASE_URL}/api/categories", headers=headers)
    print(f"\nGET /api/categories: {resp.status_code}")
    print(resp.json())

    # 创建分类
    resp = requests.post(f"{BASE_URL}/api/categories", headers=headers, json={
        "name": "热菜",
        "sort_order": 1
    })
    print(f"\nPOST /api/categories: {resp.status_code}")
    print(resp.text)

if __name__ == "__main__":
    token = login()
    test_api(token)
