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

from ..config import BROWSER_CONFIG, SCRAPER_CONFIG

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
        except TimeoutException:
            logger.warning(f"页面加载超时: {url}")
            self.refresh_page()
        except WebDriverException as e:
            logger.error(f"页面加载失败: {str(e)}")
            raise

    def refresh_page(self):
        """刷新当前页面"""
        self.driver.refresh()
        logger.info("页面已刷新")

    def scroll_to_bottom(self):
        """滚动到页面底部并等待新内容加载"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待新内容加载
                time.sleep(SCRAPER_CONFIG["scroll_pause_time"])
                
                # 计算新的滚动高度并与之前的滚动高度进行比较
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            logger.info("页面滚动完成")
        except Exception as e:
            logger.error(f"页面滚动失败: {str(e)}")
            raise

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