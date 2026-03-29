"""
文件上传服务
支持本地存储
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import UploadFile


# 上传配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


class FileUploadService:
    """文件上传服务"""

    @staticmethod
    async def upload_image(
        file: UploadFile,
        sub_dir: str = "dishes",
        max_size: int = MAX_FILE_SIZE
    ) -> dict:
        """
        上传图片

        Args:
            file: 上传的文件
            sub_dir: 子目录
            max_size: 最大文件大小

        Returns:
            {
                "filename": "xxx.jpg",
                "url": "/uploads/dishes/xxx.jpg",
                "path": "/full/path/to/xxx.jpg"
            }

        Raises:
            ValueError: 文件类型不支持或文件过大
        """
        # 检查文件类型
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"不支持的文件类型: {file.content_type}，仅支持: JPEG, PNG, GIF, WEBP")

        # 读取文件内容
        content = await file.read()

        # 检查文件大小
        if len(content) > max_size:
            raise ValueError(f"文件过大，最大支持 {max_size // (1024 * 1024)}MB")

        # 生成唯一文件名
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建子目录
        today = datetime.now().strftime("%Y%m")
        upload_path = UPLOAD_DIR / sub_dir / today
        upload_path.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = upload_path / filename
        with open(file_path, "wb") as f:
            f.write(content)

        # 返回相对路径
        relative_url = f"/uploads/{sub_dir}/{today}/{filename}"

        return {
            "filename": filename,
            "url": relative_url,
            "path": str(file_path),
            "size": len(content),
            "content_type": file.content_type
        }

    @staticmethod
    def delete_file(relative_url: str) -> bool:
        """
        删除文件

        Args:
            relative_url: 文件相对路径 (如 /uploads/dishes/202603/xxx.jpg)

        Returns:
            是否删除成功
        """
        try:
            # 安全检查：只允许删除 uploads 目录下的文件
            if not relative_url.startswith("/uploads/"):
                return False

            file_path = UPLOAD_DIR.parent / relative_url.lstrip("/")
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_path(relative_url: str) -> Optional[str]:
        """
        获取文件的完整路径

        Args:
            relative_url: 文件相对路径

        Returns:
            完整路径，如果文件不存在返回 None
        """
        file_path = UPLOAD_DIR.parent / relative_url.lstrip("/")
        if file_path.exists():
            return str(file_path)
        return None
