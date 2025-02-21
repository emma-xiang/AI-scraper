"""
配置文件，存储爬虫程序的基本设置
"""
from pathlib import Path

# 基础配置
BASE_URL = "https://www.toolify.ai/"
DATA_DIR = Path(__file__).parent / "data"
TOOLS_CSV = DATA_DIR / "tools.csv"

# 浏览器配置
BROWSER_CONFIG = {
    "headless": True,  # 无头模式运行
    "page_load_timeout": 60,  # 页面加载超时时间（秒）
    "implicit_wait": 30,  # 隐式等待时间（秒）
}

# 爬虫配置
SCRAPER_CONFIG = {
    "scroll_pause_time": 5,  # 滚动等待时间（秒）
    "max_retries": 5,  # 最大重试次数
    "batch_size": 100,  # 每批处理的工具数量
    "target_tools": 500,  # 目标工具数量
    "load_wait_time": 10,  # 页面初始加载等待时间（秒）
}

# 数据存储配置
STORAGE_CONFIG = {
    "csv_encoding": "utf-8",
    "csv_columns": [
        "tool_name",
        "description",
        "url",
        "category",
        "added_date"
    ]
}

# 日志配置
LOG_CONFIG = {
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "level": "INFO"
}