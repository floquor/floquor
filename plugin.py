import os
import importlib
import time
from app import app

import logging


def load_plugins():
    """动态地从plugins目录中加载所有插件

    遍历plugins目录下的所有文件夹，如果文件夹中包含__init__.py文件，
    则将其作为插件模块进行导入。
    """
    # 获取plugins目录的绝对路径
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")

    # 确保plugins目录存在
    if not os.path.exists(plugins_dir):
        return

    # 遍历plugins目录下的所有项目
    for item in os.listdir(plugins_dir):
        # 构建完整路径
        item_path = os.path.join(plugins_dir, item)

        # 检查是否是目录
        if not os.path.isdir(item_path):
            continue

        # 检查是否包含__init__.py文件
        init_file = os.path.join(item_path, "__init__.py")
        if not os.path.exists(init_file):
            continue

        # 导入插件模块
        # 模块名格式为 plugins.{文件夹名}
        module_name = f"plugins.{item}"
        try:
            logging.info(f"Start loading plugin {item}")
            start_time = time.time()
            importlib.import_module(module_name)
            end_time = time.time()
            logging.info(
                f"Plugin {item} loaded successfully in {end_time - start_time:.2f} seconds"
            )

        except Exception as e:
            logging.error(f"Error loading plugin {item}: {str(e)}")
