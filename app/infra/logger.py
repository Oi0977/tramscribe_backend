# app/infra/logger.py （通用日志配置，全项目复用）
import logging
from logging.handlers import RotatingFileHandler
import os
from app.infra.config import PROJECT_ROOT

def get_logger(name: str) -> logging.Logger:
    LOG_DIR = str(PROJECT_ROOT / 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:  # 避免重复添加处理器
        return logger
    # 禁止日志向上传递（避免父日志器重复打印）
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 控制台
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    # 文件
    file = RotatingFileHandler(os.path.join(LOG_DIR, f"{name}.log"), maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)
    return logger