"""
@Description :   测试文件
@Author      :   XiaoYuan
@Time        :   2025/09/23 15:09:28
"""
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_serve():
    response = client.get("/react")
    assert "application/json" in response.headers.get("content-type")

    response = client.get("/vue@3.3.4")
    assert response.status_code == 404
