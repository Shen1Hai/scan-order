"""
日志配置模块
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)

    # 文件处理器 (按天滚动)
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # 错误文件处理器
    error_handler = RotatingFileHandler(
        LOG_DIR / f"{name}_error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# 应用日志记录器
app_logger = setup_logger("app")

# API 请求日志记录器
api_logger = setup_logger("api")

# 数据库日志记录器
db_logger = setup_logger("db")

# WebSocket 日志记录器
ws_logger = setup_logger("websocket")


class RequestLogger:
    """请求日志中间件"""

    def __init__(self, logger):
        self.logger = logger

    def log_request(self, request, response=None, error=None):
        """记录请求日志"""
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        }

        if response:
            log_data["status"] = response.status_code

        if error:
            log_data["error"] = str(error)
            self.logger.error(f"Request failed: {log_data}", exc_info=error)
        else:
            self.logger.info(f"Request: {log_data}")


request_logger = RequestLogger(api_logger)
