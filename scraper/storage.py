"""
数据存储模块，负责将工具信息保存到CSV文件
"""
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import List, Dict
import os

from ..config import STORAGE_CONFIG, TOOLS_CSV

class DataStorage:
    """数据存储管理器"""
    
    def __init__(self):
        """初始化数据存储管理器"""
        self.csv_path = TOOLS_CSV
        self._ensure_data_dir()
        
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
    def save_tools(self, tools: List[Dict[str, str]], mode: str = 'a') -> bool:
        """
        保存工具信息到CSV文件
        
        Args:
            tools: 工具信息列表
            mode: 写入模式，'a'为追加，'w'为覆盖
            
        Returns:
            保存是否成功
        """
        try:
            if not tools:
                logger.warning("没有工具信息需要保存")
                return False
                
            df = pd.DataFrame(tools)
            
            # 确保列的顺序符合配置
            df = df.reindex(columns=STORAGE_CONFIG["csv_columns"])
            
            # 如果文件不存在且模式为追加，则写入表头
            header = True if mode == 'w' or not os.path.exists(self.csv_path) else False
            
            # 保存到CSV文件
            df.to_csv(
                self.csv_path,
                mode=mode,
                header=header,
                index=False,
                encoding=STORAGE_CONFIG["csv_encoding"]
            )
            
            logger.info(f"成功保存 {len(tools)} 个工具信息到 {self.csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存工具信息失败: {str(e)}")
            return False
            
    def load_existing_tools(self) -> set:
        """
        加载已存在的工具URL，用于去重
        
        Returns:
            已存在工具URL的集合
        """
        try:
            if not os.path.exists(self.csv_path):
                return set()
                
            df = pd.read_csv(
                self.csv_path,
                encoding=STORAGE_CONFIG["csv_encoding"]
            )
            return set(df['url'].unique())
            
        except Exception as e:
            logger.error(f"加载已存在工具信息失败: {str(e)}")
            return set()
            
    def backup_csv(self) -> bool:
        """
        备份CSV文件
        
        Returns:
            备份是否成功
        """
        try:
            if not os.path.exists(self.csv_path):
                return False
                
            backup_path = str(self.csv_path) + '.bak'
            pd.read_csv(
                self.csv_path,
                encoding=STORAGE_CONFIG["csv_encoding"]
            ).to_csv(
                backup_path,
                index=False,
                encoding=STORAGE_CONFIG["csv_encoding"]
            )
            
            logger.info(f"成功备份CSV文件到 {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"备份CSV文件失败: {str(e)}")
            return False
            
    def merge_duplicates(self) -> bool:
        """
        合并CSV文件中的重复记录
        
        Returns:
            合并是否成功
        """
        try:
            if not os.path.exists(self.csv_path):
                return False
                
            df = pd.read_csv(
                self.csv_path,
                encoding=STORAGE_CONFIG["csv_encoding"]
            )
            
            # 删除完全重复的行
            df_cleaned = df.drop_duplicates()
            
            # 基于URL去重，保留最新的记录
            df_cleaned = df_cleaned.sort_values('added_date').drop_duplicates(
                subset=['url'],
                keep='last'
            )
            
            # 保存清理后的数据
            df_cleaned.to_csv(
                self.csv_path,
                index=False,
                encoding=STORAGE_CONFIG["csv_encoding"]
            )
            
            removed_count = len(df) - len(df_cleaned)
            logger.info(f"成功移除 {removed_count} 条重复记录")
            return True
            
        except Exception as e:
            logger.error(f"合并重复记录失败: {str(e)}")
            return False