"""
工业风窗口 - 灰白配色、方角按钮、大字号、工厂风格

特点：
- 灰色背景 + 白色控件
- 无圆角（方角）
- 大字号标签
- 清晰的边框分隔
- 工业控制台风格
"""

from ui.base_window import BaseWindow


class IndustrialWindow(BaseWindow):
    """工业风主窗口"""

    def _get_stylesheet(self) -> str:
        return """
/* ========== 全局 ========== */
QMainWindow {
    background-color: #E8E8E8;
}
QWidget {
    font-family: "Microsoft YaHei", "SimSun", sans-serif;
    font-size: 13px;
    color: #222222;
}

/* ========== 分组框 ========== */
QGroupBox {
    border: 2px solid #888888;
    background-color: #F0F0F0;
    font-size: 14px;
    font-weight: bold;
    color: #333333;
    padding: 14px 8px 8px 8px;
    margin-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #444444;
}

/* ========== 按钮 - 通用 ========== */
QPushButton {
    background-color: #D8D8D8;
    color: #222222;
    border: 1px solid #888888;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: bold;
    min-width: 72px;
}
QPushButton:hover {
    background-color: #CCCCCC;
    border-color: #666666;
}
QPushButton:pressed {
    background-color: #B0B0B0;
}
QPushButton:disabled {
    background-color: #E8E8E8;
    color: #AAAAAA;
    border-color: #BBBBBB;
}

/* 打开串口按钮 */
QPushButton#btnOpen {
    background-color: #C8E6C9;
    border-color: #666666;
    min-width: 90px;
}
QPushButton#btnOpen:hover {
    background-color: #A5D6A7;
}

/* 关闭串口按钮 */
QPushButton#btnClose {
    background-color: #FFCDD2;
    border-color: #666666;
    min-width: 90px;
}
QPushButton#btnClose:hover {
    background-color: #EF9A9A;
}

/* 发送按钮 */
QPushButton#btnSend {
    background-color: #90CAF9;
    color: #111111;
    border: 2px solid #555555;
    font-size: 18px;
    font-weight: bold;
}
QPushButton#btnSend:hover {
    background-color: #64B5F6;
}
QPushButton#btnSend:pressed {
    background-color: #42A5F5;
}

/* 微调按钮 */
QPushButton#stepBtn {
    min-width: 48px;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: bold;
    background-color: #E0E0E0;
}

/* ========== 下拉框 ========== */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #888888;
    padding: 4px 8px;
    font-size: 13px;
    min-width: 80px;
    color: #222222;
}
QComboBox:hover {
    border-color: #555555;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #888888;
    selection-background-color: #BDBDBD;
    color: #222222;
}

/* ========== 输入框 ========== */
QLineEdit {
    background-color: #FFFFFF;
    border: 2px solid #888888;
    padding: 6px 10px;
    font-size: 13px;
    color: #222222;
}
QLineEdit:focus {
    border-color: #555555;
    background-color: #FFFFF0;
}

/* 数据输入框 */
QLineEdit#dataInput {
    border: 3px solid #666666;
    background-color: #FAFAFA;
    font-size: 42px;
    font-weight: bold;
    color: #111111;
}

/* ========== 日志区 ========== */
QTextEdit#logText {
    background-color: #FAFAFA;
    border: 2px solid #888888;
    color: #333333;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12pt;
}
"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Writer Tool")
