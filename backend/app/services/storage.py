"""
存储服务 - 策略模式
支持多种存储后端: 本地、MinIO、阿里OSS、腾讯COS等
"""
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile


# 配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class BaseStorage(ABC):
    """存储抽象基类"""

    @abstractmethod
    async def upload(self, file: UploadFile, sub_dir: str) -> dict:
        """上传文件，返回 {url, filename}"""
        pass

    @abstractmethod
    def delete(self, url: str) -> bool:
        """删除文件"""
        pass

    @abstractmethod
    def get_url(self, filename: str) -> str:
        """获取文件访问URL"""
        pass


class LocalStorage(BaseStorage):
    """本地存储"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    async def upload(self, file: UploadFile, sub_dir: str = "dishes") -> dict:
        # 检查文件类型
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"不支持的文件类型: {file.content_type}")

        # 读取文件
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"文件过大，最大支持 {MAX_FILE_SIZE // (1024 * 1024)}MB")

        # 生成文件名
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建目录
        today = datetime.now().strftime("%Y%m")
        upload_path = UPLOAD_DIR / sub_dir / today
        upload_path.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = upload_path / filename
        with open(file_path, "wb") as f:
            f.write(content)

        url = f"/uploads/{sub_dir}/{today}/{filename}"

        return {
            "url": url,
            "filename": filename,
            "path": str(file_path)
        }

    def delete(self, url: str) -> bool:
        if not url.startswith("/uploads/"):
            return False
        file_path = UPLOAD_DIR.parent / url.lstrip("/")
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_url(self, filename: str) -> str:
        return f"{self.base_url}/uploads/{filename}"


class MinIOStorage(BaseStorage):
    """
    MinIO 对象存储
    需要配置: MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
    """

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket: str = "scanorder",
        secure: bool = False
    ):
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "")
        self.bucket = bucket
        self.secure = secure
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from minio import Minio
            self._client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            # 确保 bucket 存在
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
        return self._client

    async def upload(self, file: UploadFile, sub_dir: str = "dishes") -> dict:
        # 检查文件类型
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"不支持的文件类型: {file.content_type}")

        # 读取文件
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"文件过大，最大支持 {MAX_FILE_SIZE // (1024 * 1024)}MB")

        # 生成文件名
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        object_name = f"{sub_dir}/{datetime.now().strftime('%Y%m')}/{filename}"

        # 上传到 MinIO
        from io import BytesIO
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(content),
            len(content),
            content_type=file.content_type
        )

        # 生成访问URL (presigned)
        url = self.client.presigned_get_object(self.bucket, object_name)

        return {
            "url": url,
            "filename": filename,
            "object_name": object_name
        }

    def delete(self, url: str) -> bool:
        # 从URL中提取object_name
        try:
            # url 格式: http://endpoint/bucket/object_name 或 presigned URL
            object_name = url.split(f"{self.bucket}/")[-1].split("?")[0]
            self.client.remove_object(self.bucket, object_name)
            return True
        except Exception:
            return False

    def get_url(self, filename: str) -> str:
        return self.client.presigned_get_object(self.bucket, filename)


class AliyunOSSStorage(BaseStorage):
    """
    阿里云OSS存储
    需要配置: ALIYUN_OSS_ENDPOINT, ALIYUN_OSS_ACCESS_KEY, ALIYUN_OSS_SECRET_KEY, ALIYUN_OSS_BUCKET
    """

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket: str = "scanorder"
    ):
        self.endpoint = endpoint or os.getenv("ALIYUN_OSS_ENDPOINT", "")
        self.access_key = access_key or os.getenv("ALIYUN_OSS_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("ALIYUN_OSS_SECRET_KEY", "")
        self.bucket = bucket
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import oss2
            auth = oss2.Auth(self.access_key, self.secret_key)
            self._client = oss2.Bucket(auth, self.endpoint, self.bucket)
        return self._client

    async def upload(self, file: UploadFile, sub_dir: str = "dishes") -> dict:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"不支持的文件类型: {file.content_type}")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise ValueError(f"文件过大，最大支持 {MAX_FILE_SIZE // (1024 * 1024)}MB")

        ext = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        object_name = f"{sub_dir}/{datetime.now().strftime('%Y%m')}/{filename}"

        self.client.put_object(object_name, content, content_type=file.content_type)

        url = f"https://{self.bucket}.{self.endpoint}/{object_name}"

        return {
            "url": url,
            "filename": filename,
            "object_name": object_name
        }

    def delete(self, url: str) -> bool:
        try:
            object_name = url.split(f"{self.bucket}.{self.endpoint}/")[-1]
            self.client.delete_object(object_name)
            return True
        except Exception:
            return False

    def get_url(self, filename: str) -> str:
        return f"https://{self.bucket}.{self.endpoint}/{filename}"


# 存储工厂 - 根据配置选择存储后端
def get_storage() -> BaseStorage:
    """
    获取存储实例

    环境变量:
    - STORAGE_TYPE: 存储类型 (local/minio/aliyun)
    - MINIO_ENDPOINT 等: 各存储的配置
    """
    storage_type = os.getenv("STORAGE_TYPE", "local")

    if storage_type == "minio":
        return MinIOStorage()
    elif storage_type == "aliyun":
        return AliyunOSSStorage()
    else:
        # 默认本地存储
        base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
        return LocalStorage(base_url)


# 全局实例
storage = get_storage()
