"""
主程序入口，整合所有模块实现完整的爬虫功能
"""
import sys
import time
from loguru import logger
from selenium.common.exceptions import WebDriverException

from config import BASE_URL, SCRAPER_CONFIG
from scraper.browser import BrowserManager
from scraper.parser import ToolParser
from scraper.storage import DataStorage

def setup_logger():
    """配置日志记录器"""
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    logger.add(
        "scraper.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG"
    )

def main():
    """主程序入口"""
    setup_logger()
    logger.info("开始运行工具爬虫程序")
    
    # 初始化组件
    browser = None
    storage = DataStorage()
    existing_tools = storage.load_existing_tools()
    
    try:
        # 初始化浏览器
        browser = BrowserManager()
        
        # 访问目标网站
        browser.get_page(BASE_URL)
        logger.info("成功访问目标网站")
        
        # 备份现有数据
        storage.backup_csv()
        
        # 滚动加载直到达到目标工具数量
        target_reached = browser.scroll_until_count(SCRAPER_CONFIG["target_tools"])
        if not target_reached:
            logger.warning(f"未能达到目标工具数量 {SCRAPER_CONFIG['target_tools']}")
        
        # 获取页面内容并解析
        page_source = browser.driver.page_source
        tools = ToolParser.parse_tool_cards(page_source)
        
        if not tools:
            logger.error("未能解析到任何工具信息")
            return
        
        # 过滤已存在的工具
        new_tools = [
            tool for tool in tools
            if tool['url'] not in existing_tools
        ]
        
        if new_tools:
            # 保存新工具信息
            storage.save_tools(new_tools, mode='a')
            logger.info(f"成功保存 {len(new_tools)} 个新工具")
            
            # 合并重复记录
            storage.merge_duplicates()
            
            logger.info(f"爬虫程序完成，共抓取 {len(tools)} 个工具，新增 {len(new_tools)} 个工具")
        else:
            logger.info("没有发现新的工具")
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        raise
        
    finally:
        # 清理资源
        if browser:
            browser.quit()

if __name__ == "__main__":
    main()