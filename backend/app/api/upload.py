from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.security import get_current_user
from app.models.staff import Staff
from app.services.storage import storage

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

# 配置静态文件服务 (本地存储)
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Staff = Depends(get_current_user)
):
    """
    上传图片
    支持 JPEG, PNG, GIF, WEBP 格式
    最大 5MB
    """
    try:
        result = await storage.upload(file=file, sub_dir="dishes")
        return {
            "success": True,
            "url": result["url"],
            "filename": result["filename"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: Staff = Depends(get_current_user)
):
    """
    上传头像
    """
    try:
        result = await storage.upload(file=file, sub_dir="avatars")
        return {
            "success": True,
            "url": result["url"],
            "filename": result["filename"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
