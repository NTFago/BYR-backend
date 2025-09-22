"""
@Description :   日志系统
@Author      :   XiaoYuan
@Time        :   2025/09/22 19:59:37
"""
import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "npm_proxy.log")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name: str = "npm_proxy") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 最低日志级别

    if logger.handlers:  # 避免重复添加 handler
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 文件输出（每天一个文件，保留 7 天）
    file_handler = TimedRotatingFileHandler(
        LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 绑定
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 默认 logger
logger = setup_logger()
