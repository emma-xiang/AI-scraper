"""
页面解析模块，负责从页面中提取工具信息
"""
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from loguru import logger
from typing import List, Dict, Optional
import re
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            if not html_content:
                logger.warning("HTML内容为空")
                return []
                
            soup = BeautifulSoup(html_content, 'html.parser')
            if not soup:
                logger.warning("HTML解析失败")
                return []
            
            # 查找所有可能的工具卡片
            tool_cards = []
            
            # 尝试多种选择器
            selectors = [
                lambda tag: tag.name == 'div' and tag.find('a') and tag.find('p'),
                lambda tag: tag.name == 'div' and tag.find(['h2', 'h3', 'h4']) and tag.find('a'),
                lambda tag: tag.name == 'div' and tag.find('a', href=True) and len(tag.find_all('p')) > 0
            ]
            
            for selector in selectors:
                cards = soup.find_all(selector)
                if cards:
                    tool_cards.extend(cards)
                    logger.info(f"使用选择器找到 {len(cards)} 个工具卡片")
            
            # 去重
            tool_cards = list(set(tool_cards))
            
            if not tool_cards:
                logger.warning("未找到任何工具卡片")
                return []
            
            # 解析每个卡片
            for card in tool_cards:
                try:
                    tool_info = ToolParser._parse_single_card(card)
                    if tool_info:
                        tools.append(tool_info)
                except Exception as e:
                    logger.warning(f"解析单个卡片失败: {str(e)}")
                    continue
            
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
            if not card:
                return None
                
            # 提取工具名称和链接
            tool_name = ""
            url = ""
            
            # 尝试从标题获取名称
            title_element = card.find(['h2', 'h3', 'h4'])
            if title_element:
                tool_name = title_element.get_text(strip=True)
            
            # 如果没有找到标题，尝试从链接文本获取
            if not tool_name:
                link_element = card.find('a')
                if link_element:
                    tool_name = link_element.get_text(strip=True)
                    url = link_element.get('href', '')
            
            # 提取工具描述
            description = ""
            paragraphs = card.find_all('p')
            if paragraphs:
                # 过滤掉太短的段落和可能的标签文本
                valid_paragraphs = [
                    p.get_text(strip=True) for p in paragraphs
                    if len(p.get_text(strip=True)) > 20  # 假设描述至少20个字符
                ]
                if valid_paragraphs:
                    # 选择最长的段落作为描述
                    description = max(valid_paragraphs, key=len)
            
            # 提取分类
            category = ""
            for element in card.find_all(['span', 'div']):
                text = element.get_text(strip=True).lower()
                if any(keyword in text for keyword in ['category:', 'type:', '类别:', '分类:']):
                    category = text.split(':', 1)[-1].strip()
                    break
            
            # 提取日期
            added_date = ""
            for element in card.find_all(['span', 'div']):
                text = element.get_text(strip=True).lower()
                if any(keyword in text for keyword in ['added:', 'date:', '添加:', '日期:']):
                    added_date = text.split(':', 1)[-1].strip()
                    break
            
            # 清理和验证数据
            tool_name = ToolParser.clean_text(tool_name)
            description = ToolParser.clean_text(description)
            url = ToolParser.validate_url(url)
            
            # 只返回有效的工具信息
            if tool_name and url:  # 描述可能为空
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
        清理文本内容，去除多余的空白字符和特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        # 去除多余空白字符
        text = " ".join(text.split())
        # 保留基本标点符号和常用特殊字符
        text = re.sub(r'[^\w\s\-.,!?()&/@#$%+]', '', text)
        return text.strip()

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
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://www.toolify.ai' + url.lstrip('/')
        return url