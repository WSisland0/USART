"""
配置管理模块 - 持久化保存/加载用户设置

保存为 JSON 文件，包括：
- 串口参数（端口号、波特率、数据位、校验位、停止位）
- UI 风格（industrial / modern）
- 接收数据显示模式（hex / ascii）
"""

import json
import os
from pathlib import Path
from typing import Any


# 默认配置
DEFAULT_CONFIG: dict[str, Any] = {
    "port": "",
    "baud_rate": 9600,
    "data_bits": 8,
    "parity": "None",
    "stop_bits": 1,
    "style": "modern",
    "receive_mode": "hex",  # hex 或 ascii
}

# 配置文件路径（相对于可执行文件所在目录）
_CONFIG_FILENAME = "config.json"


def _get_config_path() -> Path:
    """获取配置文件完整路径"""
    return Path(_CONFIG_FILENAME)


def load_config() -> dict[str, Any]:
    """
    从 config.json 加载配置。
    如果文件不存在或损坏，返回默认配置。

    返回:
        配置字典
    """
    config_path = _get_config_path()
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        # 合并默认值，确保所有键都存在
        config = DEFAULT_CONFIG.copy()
        config.update(loaded)
        return config
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> bool:
    """
    将配置保存到 config.json。

    参数:
        config: 配置字典

    返回:
        成功返回 True，失败返回 False
    """
    config_path = _get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except IOError as e:
        print(f"[ConfigManager] 保存配置失败: {e}")
        return False
