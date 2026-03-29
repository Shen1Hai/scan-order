"""
扫码点单系统 - FastAPI 后端
运行: uvicorn main:app --reload --port 8000
"""
import uvicorn
from app.index import app

if __name__ == "__main__":
    uvicorn.run(
        "app.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
