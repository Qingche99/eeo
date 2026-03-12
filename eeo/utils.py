# -*- coding: utf-8 -*-
"""
@Author   : 清澈
@Time     :2026/1/15
@File     :utils.py
@IDE      :PyCharm
"""


import hashlib
import time
from typing import Dict, Any
import logging

"""
ClassIn API工具函数
"""

logger = logging.getLogger(__name__)


class SignatureUtils:
    """签名工具类"""

    @staticmethod
    def generate_safe_key(secret: str, timestamp: int = None) -> tuple:
        """
        生成安全密钥

        Args:
            secret: 密钥
            timestamp: 时间戳，如果为None则使用当前时间

        Returns:
            tuple: (timestamp, safeKey)
        """
        if timestamp is None:
            timestamp = int(time.time())
        safe_key = hashlib.md5(f'{secret}{timestamp}'.encode()).hexdigest()
        return timestamp, safe_key

    @staticmethod
    def generate_v2_signature(payload: Dict[str, Any], sid: str, secret: str) -> Dict[str, str]:
        """
        生成v2 headers接口签名

        Args:
            payload: 请求数据
            sid: 学校ID
            secret: 密钥

        Returns:
            Dict: 签名头部信息
        """
        timestamp = int(time.time())

        # 过滤掉列表、字典或过长的字符串
        filtered_data = {
            k: v for k, v in payload.items()
            if v is not None and not isinstance(v, (list, dict)) and len(str(v)) <= 1024
        }
        filtered_data['sid'] = sid
        filtered_data['timeStamp'] = timestamp

        # 排序并构建签名字符串
        sorted_items = sorted(filtered_data.items())
        sign_string = "&".join(f"{key}={value}" for key, value in sorted_items)
        sign_string += f"&key={secret}"

        # 计算签名
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        return {
            'X-EEO-SIGN': sign,
            'X-EEO-UID': sid,
            'X-EEO-TS': str(timestamp),
            'Content-Type': 'application/json'
        }


class RequestUtils:
    """请求工具类"""

    @staticmethod
    def prepare_request_data(base_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        准备请求数据

        Args:
            base_data: 基础数据
            **kwargs: 额外参数

        Returns:
            Dict: 处理后的请求数据
        """
        data = {**base_data, **kwargs}

        # 移除值为None的参数
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def validate_response(response) -> Dict[str, Any]:
        """
        验证响应

        Args:
            response: requests.Response对象

        Returns:
            Dict: 解析后的JSON数据

        Raises:
            ValueError: 如果响应不是有效的JSON
        """
        try:
            return response.json()
        except ValueError as e:
            logger.error(f"解析响应失败: {e}, 响应内容: {response.text}")
            raise ValueError(f"无效的响应格式: {response.status_code}, {response.text}") from e
