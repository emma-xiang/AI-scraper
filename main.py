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
        
        tools_count = 0
        retry_count = 0
        
        while retry_count < SCRAPER_CONFIG["max_retries"]:
            try:
                # 滚动加载更多内容
                browser.scroll_to_bottom()
                
                # 获取页面内容并解析
                page_source = browser.driver.page_source
                tools = ToolParser.parse_tool_cards(page_source)
                
                # 过滤已存在的工具
                new_tools = [
                    tool for tool in tools
                    if tool['url'] not in existing_tools
                ]
                
                if new_tools:
                    # 保存新工具信息
                    storage.save_tools(new_tools, mode='a')
                    tools_count += len(new_tools)
                    existing_tools.update(tool['url'] for tool in new_tools)
                    logger.info(f"当前已抓取 {tools_count} 个工具")
                    
                    # 批量处理，达到批次大小后暂停
                    if tools_count % SCRAPER_CONFIG["batch_size"] == 0:
                        logger.info("达到批次大小，暂停处理")
                        time.sleep(SCRAPER_CONFIG["scroll_pause_time"] * 2)
                
                # 如果没有新工具，可能已经到达底部
                if not new_tools:
                    logger.info("没有发现新的工具，可能已到达底部")
                    break
                    
            except WebDriverException as e:
                retry_count += 1
                logger.warning(f"出现异常，重试 ({retry_count}/{SCRAPER_CONFIG['max_retries']}): {str(e)}")
                if retry_count < SCRAPER_CONFIG["max_retries"]:
                    time.sleep(SCRAPER_CONFIG["scroll_pause_time"] * 2)
                    browser.refresh_page()
                else:
                    logger.error("达到最大重试次数，程序终止")
                    break
        
        # 合并重复记录
        storage.merge_duplicates()
        
        logger.info(f"爬虫程序完成，共抓取 {tools_count} 个工具")
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        raise
        
    finally:
        # 清理资源
        if browser:
            browser.quit()

if __name__ == "__main__":
    main()