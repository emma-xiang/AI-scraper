"""
页面解析模块，负责从页面中提取工具信息
"""
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from loguru import logger
from typing import List, Dict, Optional

class ToolParser:
    """工具信息解析器"""
    
    @staticmethod
    def parse_tool_cards(html_content: str) -> List[Dict[str, str]]:
        """
        解析页面中的工具卡片信息
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            工具信息列表，每个工具包含名称、描述、链接等信息
        """
        tools = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # 查找所有工具卡片元素
            tool_cards = soup.find_all('div', class_='tool-card')  # 需要根据实际HTML结构调整
            
            for card in tool_cards:
                tool_info = ToolParser._parse_single_card(card)
                if tool_info:
                    tools.append(tool_info)
            
            logger.info(f"成功解析 {len(tools)} 个工具信息")
            return tools
        except Exception as e:
            logger.error(f"解析工具卡片失败: {str(e)}")
            return []

    @staticmethod
    def _parse_single_card(card) -> Optional[Dict[str, str]]:
        """
        解析单个工具卡片
        
        Args:
            card: BeautifulSoup对象，表示单个工具卡片
            
        Returns:
            包含工具信息的字典，解析失败返回None
        """
        try:
            # 提取工具名称
            name_element = card.find('h3', class_='tool-name')  # 需要根据实际HTML结构调整
            tool_name = name_element.text.strip() if name_element else ""
            
            # 提取工具描述
            desc_element = card.find('p', class_='tool-description')  # 需要根据实际HTML结构调整
            description = desc_element.text.strip() if desc_element else ""
            
            # 提取工具链接
            link_element = card.find('a', class_='tool-link')  # 需要根据实际HTML结构调整
            url = link_element.get('href', '') if link_element else ""
            
            # 提取工具分类
            category_element = card.find('span', class_='tool-category')  # 需要根据实际HTML结构调整
            category = category_element.text.strip() if category_element else ""
            
            # 提取添加日期
            date_element = card.find('span', class_='tool-date')  # 需要根据实际HTML结构调整
            added_date = date_element.text.strip() if date_element else ""
            
            # 只返回非空的工具信息
            if tool_name and description and url:
                return {
                    'tool_name': tool_name,
                    'description': description,
                    'url': url,
                    'category': category,
                    'added_date': added_date
                }
            return None
            
        except Exception as e:
            logger.warning(f"解析单个工具卡片失败: {str(e)}")
            return None

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本内容，去除多余的空白字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        return " ".join(text.split())

    @staticmethod
    def validate_url(url: str) -> str:
        """
        验证并规范化URL
        
        Args:
            url: 原始URL
            
        Returns:
            规范化后的URL
        """
        if not url:
            return ""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url