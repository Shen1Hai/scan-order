from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "扫码点单系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 8000

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres123"
    DB_NAME: str = "scanorder"

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接 URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # CORS 配置
    CORS_ORIGINS: str = "*"

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """CORS 源列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
