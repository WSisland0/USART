"""
日志模块 - 管理串口通信日志

支持四种日志类别：
- TX (发送): 蓝色
- RX (接收): 绿色
- ERROR (错误): 红色
- INFO (系统): 灰色

每条日志包含时间戳、类别和消息。
"""

from datetime import datetime
from enum import Enum
from typing import Callable

from PySide6.QtCore import QObject, Signal


class LogCategory(Enum):
    """日志类别枚举"""
    TX = "TX"
    RX = "RX"
    ERROR = "ERROR"
    INFO = "INFO"


class LogEntry:
    """单条日志记录"""

    def __init__(self, category: LogCategory, message: str):
        self.timestamp = datetime.now()
        self.category = category
        self.message = message

    def formatted(self) -> str:
        """
        格式化输出。

        返回:
            [HH:MM:SS] TX -> message
            [HH:MM:SS] RX <- message
            [HH:MM:SS] ERROR message
            [HH:MM:SS] INFO message
        """
        ts = self.timestamp.strftime("%H:%M:%S")
        cat = self.category.value
        if cat == "TX":
            return f"[{ts}] TX -> {self.message}"
        elif cat == "RX":
            return f"[{ts}] RX <- {self.message}"
        else:
            return f"[{ts}] {cat} {self.message}"


class LogManager(QObject):
    """日志管理器 - 发射信号通知 UI 更新"""

    # 新日志条目信号
    entry_added = Signal(LogEntry)
    # 清空信号
    cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: list[LogEntry] = []

    def add_entry(self, category: LogCategory, message: str):
        """添加一条日志并发射信号"""
        entry = LogEntry(category, message)
        self._entries.append(entry)
        self.entry_added.emit(entry)

    def add_tx(self, message: str):
        """添加发送日志"""
        self.add_entry(LogCategory.TX, message)

    def add_rx(self, message: str):
        """添加接收日志"""
        self.add_entry(LogCategory.RX, message)

    def add_error(self, message: str):
        """添加错误日志"""
        self.add_entry(LogCategory.ERROR, message)

    def add_info(self, message: str):
        """添加系统日志"""
        self.add_entry(LogCategory.INFO, message)

    def clear(self):
        """清空所有日志并通知 UI"""
        self._entries.clear()
        self.cleared.emit()

    def get_entries(self) -> list[LogEntry]:
        """返回所有日志条目"""
        return list(self._entries)

    def save_to_file(self, filepath: str) -> bool:
        """
        将日志保存到文件。

        参数:
            filepath: 保存路径

        返回:
            成功返回 True
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for entry in self._entries:
                    f.write(entry.formatted() + "\n")
            return True
        except IOError as e:
            self.add_error(f"保存日志失败: {e}")
            return False
