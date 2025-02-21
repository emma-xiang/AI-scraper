"""
浏览器管理模块，负责Selenium浏览器的初始化和控制
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BROWSER_CONFIG, SCRAPER_CONFIG

class BrowserManager:
    def __init__(self):
        """初始化浏览器管理器"""
        self.driver = None
        self.wait = None
        self._setup_browser()

    def _setup_browser(self):
        """设置并初始化Chrome浏览器"""
        try:
            options = Options()
            if BROWSER_CONFIG["headless"]:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.driver.set_page_load_timeout(BROWSER_CONFIG["page_load_timeout"])
            self.driver.implicitly_wait(BROWSER_CONFIG["implicit_wait"])
            self.wait = WebDriverWait(self.driver, BROWSER_CONFIG["implicit_wait"])
            
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            raise

    def get_page(self, url):
        """加载指定URL的页面"""
        try:
            self.driver.get(url)
            logger.info(f"成功加载页面: {url}")
            
            # 注入自动滚动脚本
            self._inject_auto_scroll_script()
            
            # 等待页面完全加载
            time.sleep(SCRAPER_CONFIG["load_wait_time"])
            
            # 尝试查找包含链接的div元素
            self._wait_for_content()
            
        except TimeoutException:
            logger.warning(f"页面加载超时: {url}")
            self.refresh_page()
        except WebDriverException as e:
            logger.error(f"页面加载失败: {str(e)}")
            raise

    def _inject_auto_scroll_script(self):
        """注入自动滚动脚本"""
        script = """
        window.autoScroll = function(step, interval) {
            function scroll() {
                let scrollHeight = document.documentElement.scrollHeight;
                let currentScroll = window.pageYOffset;
                let newScroll = Math.min(currentScroll + step, scrollHeight);
                window.scrollTo(0, newScroll);
                return newScroll < scrollHeight;
            }
            
            return new Promise((resolve) => {
                let timer = setInterval(() => {
                    if (!scroll()) {
                        clearInterval(timer);
                        resolve();
                    }
                }, interval);
            });
        };
        """
        self.driver.execute_script(script)

    def _wait_for_content(self):
        """等待内容加载并返回找到的卡片数量"""
        try:
            # 等待任意工具卡片出现
            self.wait.until(lambda d: len(d.find_elements(By.XPATH, "//div[.//a and .//p]")) > 0)
            cards = self.driver.find_elements(By.XPATH, "//div[.//a and .//p]")
            logger.info(f"找到 {len(cards)} 个可能的工具卡片")
            return len(cards)
        except TimeoutException:
            logger.warning("等待内容加载超时")
            return 0

    def refresh_page(self):
        """刷新当前页面"""
        self.driver.refresh()
        time.sleep(SCRAPER_CONFIG["scroll_pause_time"])
        logger.info("页面已刷新")
        self._wait_for_content()

    def scroll_to_bottom(self):
        """
        使用JavaScript滚动到页面底部并等待新内容加载
        返回是否成功加载新内容
        """
        try:
            # 获取当前工具卡片数量
            initial_cards = len(self.driver.find_elements(By.XPATH, "//div[.//a and .//p]"))
            initial_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 使用注入的自动滚动脚本
            self.driver.execute_script("return window.autoScroll(100, 50)")  # 每50ms滚动100px
            time.sleep(SCRAPER_CONFIG["scroll_pause_time"])
            
            # 等待新内容加载
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            new_cards = len(self.driver.find_elements(By.XPATH, "//div[.//a and .//p]"))
            
            # 检查是否加载了新内容
            if new_height > initial_height or new_cards > initial_cards:
                logger.info(f"成功加载新内容，当前工具数量: {new_cards}")
                return True
            else:
                logger.info("没有加载到新内容")
                return False
                
        except Exception as e:
            logger.error(f"页面滚动失败: {str(e)}")
            return False

    def scroll_until_count(self, target_count):
        """
        持续滚动直到达到目标工具数量或无法加载更多
        
        Args:
            target_count: 目标工具数量
            
        Returns:
            bool: 是否达到目标数量
        """
        retry_count = 0
        no_new_content_count = 0
        
        while retry_count < SCRAPER_CONFIG["max_retries"]:
            try:
                current_count = len(self.driver.find_elements(By.XPATH, "//div[.//a and .//p]"))
                logger.info(f"当前已加载工具数量: {current_count}")
                
                if current_count >= target_count:
                    logger.info(f"已达到目标工具数量: {current_count}")
                    return True
                
                # 尝试点击"加载更多"按钮（如果存在）
                try:
                    load_more = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), '加载更多')]")
                    load_more.click()
                    time.sleep(SCRAPER_CONFIG["scroll_pause_time"])
                    logger.info("点击了加载更多按钮")
                except:
                    pass
                
                # 滚动并检查是否有新内容
                if self.scroll_to_bottom():
                    no_new_content_count = 0
                else:
                    no_new_content_count += 1
                    
                # 如果连续多次没有新内容，尝试刷新页面
                if no_new_content_count >= 2:
                    logger.warning("连续多次没有新内容，尝试刷新页面")
                    self.refresh_page()
                    no_new_content_count = 0
                    retry_count += 1
                
                time.sleep(SCRAPER_CONFIG["scroll_pause_time"])
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"滚动加载失败，重试 ({retry_count}/{SCRAPER_CONFIG['max_retries']}): {str(e)}")
                if retry_count < SCRAPER_CONFIG["max_retries"]:
                    time.sleep(SCRAPER_CONFIG["scroll_pause_time"] * 2)
                    self.refresh_page()
                else:
                    logger.error("达到最大重试次数，停止滚动")
                    break
        
        final_count = len(self.driver.find_elements(By.XPATH, "//div[.//a and .//p]"))
        return final_count >= target_count

    def wait_for_element(self, by, value, timeout=None):
        """等待元素出现在页面上"""
        timeout = timeout or BROWSER_CONFIG["implicit_wait"]
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"等待元素超时: {value}")
            return None

    def quit(self):
        """关闭浏览器并清理资源"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")
            self.driver = None