"""
现代风窗口 - 蓝白配色、圆角、阴影卡片风格

特点：
- 白色背景 + 蓝色点缀
- 圆角边框
- 轻微阴影效果
- 卡片式布局
- 更精致的视觉效果
"""

from ui.base_window import BaseWindow


class ModernWindow(BaseWindow):
    """现代风主窗口"""

    def _get_stylesheet(self) -> str:
        return """
/* ========== 全局 ========== */
QMainWindow {
    background-color: #F5F7FA;
}
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #333333;
}

/* ========== 分组框 ========== */
QGroupBox {
    border: 1px solid #DDE4EF;
    border-radius: 10px;
    background-color: #FFFFFF;
    font-size: 14px;
    font-weight: bold;
    color: #1565C0;
    padding: 16px 10px 10px 10px;
    margin-top: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #1565C0;
}

/* ========== 按钮 - 通用 ========== */
QPushButton {
    background-color: #E3F2FD;
    color: #1565C0;
    border: 1px solid #BBDEFB;
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: bold;
    min-width: 72px;
}
QPushButton:hover {
    background-color: #BBDEFB;
    border-color: #90CAF9;
}
QPushButton:pressed {
    background-color: #90CAF9;
}
QPushButton:disabled {
    background-color: #F5F5F5;
    color: #BDBDBD;
    border-color: #E0E0E0;
}

/* 打开串口按钮 */
QPushButton#btnOpen {
    background-color: #E8F5E9;
    color: #2E7D32;
    border-color: #A5D6A7;
    border-radius: 6px;
    min-width: 90px;
}
QPushButton#btnOpen:hover {
    background-color: #C8E6C9;
    border-color: #66BB6A;
}

/* 关闭串口按钮 */
QPushButton#btnClose {
    background-color: #FFEBEE;
    color: #C62828;
    border-color: #EF9A9A;
    border-radius: 6px;
    min-width: 90px;
}
QPushButton#btnClose:hover {
    background-color: #FFCDD2;
    border-color: #EF5350;
}

/* 发送按钮 */
QPushButton#btnSend {
    background-color: #1565C0;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
}
QPushButton#btnSend:hover {
    background-color: #1976D2;
}
QPushButton#btnSend:pressed {
    background-color: #0D47A1;
}

/* 微调按钮 */
QPushButton#stepBtn {
    min-width: 48px;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: bold;
    background-color: #F0F4FF;
    border-radius: 8px;
    color: #1565C0;
}
QPushButton#stepBtn:hover {
    background-color: #D6E4FF;
}

/* ========== 下拉框 ========== */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #BBDEFB;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-width: 80px;
    color: #333333;
}
QComboBox:hover {
    border-color: #64B5F6;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #BBDEFB;
    border-radius: 4px;
    selection-background-color: #E3F2FD;
    selection-color: #1565C0;
    color: #333333;
}

/* ========== 输入框 ========== */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #DDE4EF;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    color: #333333;
}
QLineEdit:focus {
    border-color: #64B5F6;
    background-color: #FAFCFF;
}

/* 数据输入框 */
QLineEdit#dataInput {
    border: 2px solid #BBDEFB;
    border-radius: 10px;
    background-color: #FAFCFF;
    font-size: 42px;
    font-weight: bold;
    color: #1565C0;
}
QLineEdit#dataInput:focus {
    border-color: #1565C0;
    background-color: #FFFFFF;
}

/* ========== 日志区 ========== */
QTextEdit#logText {
    background-color: #FAFCFF;
    border: 1px solid #DDE4EF;
    border-radius: 6px;
    color: #333333;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
}
"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Writer Tool [现代风]")
