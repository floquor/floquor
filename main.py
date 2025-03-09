from app import app  # 确保app实例最先被导入
from plugin import load_plugins
from api_service import start_api_service
import logging
import argparse

if __name__ == "__main__":
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Start application service")
    parser.add_argument(
        "--dev", action="store_true", help="Enable development mode with CORS"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.dev:
        logging.info("Starting application in development mode")

    load_plugins()
    start_api_service(dev_mode=args.dev)
