import logging
import sys

# 配置标准日志格式
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

class Logger:
    @staticmethod
    def info(module, message):
        logging.info(f"[{module}] {message}")

    @staticmethod
    def error(module, message):
        logging.error(f"[{module}] {message}")

    @staticmethod
    def success(module, message):
        logging.info(f"[{module}] SUCCESS: {message}")

logger = Logger()