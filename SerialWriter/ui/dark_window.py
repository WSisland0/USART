"""
暗色风窗口 - Dark Mode Developer 风格

特点：
- 深蓝黑底色（Slate-900），VS Code / Terminal 风格
- 圆角边框 + 轻微层次区分
- 高对比度日志区
- 适配长时间调试使用，降低眼疲劳
"""

from ui.base_window import BaseWindow
from core.logger import LogCategory


class DarkWindow(BaseWindow):
    """暗色风主窗口 — Dark Mode Developer"""

    # 暗底适配的日志颜色
    _log_colors = {
        LogCategory.TX:    "#38BDF8",  # Sky-400 亮蓝
        LogCategory.RX:    "#4ADE80",  # Green-400 亮绿
        LogCategory.ERROR: "#F87171",  # Red-400 亮红
        LogCategory.INFO:  "#94A3B8",  # Slate-400 中灰
    }

    def _get_stylesheet(self) -> str:
        return """
/* ========== 全局 ========== */
QMainWindow {
    background-color: #0F172A;
}
QWidget {
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", "Microsoft YaHei", sans-serif;
    font-size: 13px;
    color: #F1F5F9;
}

/* ========== 分组框 ========== */
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #1E293B;
    font-size: 14px;
    font-weight: bold;
    color: #94A3B8;
    padding: 16px 10px 10px 10px;
    margin-top: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #E2E8F0;
}

/* ========== QMenu (菜单栏下拉) ========== */
QMenuBar {
    background-color: #1E293B;
    color: #E2E8F0;
    border-bottom: 1px solid #334155;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 4px 12px;
    background-color: transparent;
    color: #E2E8F0;
}
QMenuBar::item:selected {
    background-color: #334155;
    border-radius: 4px;
}
QMenu {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px;
    color: #E2E8F0;
}
QMenu::item {
    padding: 6px 28px 6px 16px;
    color: #E2E8F0;
}
QMenu::item:selected {
    background-color: #334155;
    border-radius: 4px;
}
QMenu::separator {
    height: 1px;
    background: #334155;
    margin: 4px 8px;
}

/* ========== 按钮 - 通用 ========== */
QPushButton {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: bold;
    min-width: 72px;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #64748B;
}
QPushButton:pressed {
    background-color: #475569;
}
QPushButton:disabled {
    background-color: #1E293B;
    color: #475569;
    border-color: #334155;
}

/* 打开串口按钮 */
QPushButton#btnOpen {
    background-color: #14532D;
    color: #86EFAC;
    border-color: #166534;
    border-radius: 6px;
    min-width: 90px;
}
QPushButton#btnOpen:hover {
    background-color: #166534;
    border-color: #22C55E;
}
QPushButton#btnOpen:disabled {
    background-color: #1E293B;
    color: #475569;
    border-color: #334155;
}

/* 关闭串口按钮 */
QPushButton#btnClose {
    background-color: #7F1D1D;
    color: #FCA5A5;
    border-color: #991B1B;
    border-radius: 6px;
    min-width: 90px;
}
QPushButton#btnClose:hover {
    background-color: #991B1B;
    border-color: #EF4444;
}
QPushButton#btnClose:disabled {
    background-color: #1E293B;
    color: #475569;
    border-color: #334155;
}

/* 发送按钮 */
QPushButton#btnSend {
    background-color: #1D4ED8;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    font-weight: bold;
}
QPushButton#btnSend:hover {
    background-color: #2563EB;
}
QPushButton#btnSend:pressed {
    background-color: #1E40AF;
}
QPushButton#btnSend:disabled {
    background-color: #1E293B;
    color: #475569;
    border: 1px solid #334155;
}

/* 微调按钮 */
QPushButton#stepBtn {
    min-width: 48px;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: bold;
    background-color: #1E293B;
    color: #38BDF8;
    border: 1px solid #334155;
    border-radius: 6px;
}
QPushButton#stepBtn:hover {
    background-color: #0F172A;
    border-color: #38BDF8;
    color: #7DD3FC;
}

/* ========== 下拉框 ========== */
QComboBox {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-width: 80px;
    color: #E2E8F0;
}
QComboBox:hover {
    border-color: #64748B;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    /* 暗色下拉箭头 */
    image: none;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 4px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    color: #E2E8F0;
    outline: none;
}

/* ========== 输入框 ========== */
QLineEdit {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    color: #F1F5F9;
}
QLineEdit:focus {
    border-color: #38BDF8;
    background-color: #0F172A;
}

/* 数据输入框 */
QLineEdit#dataInput {
    border: 2px solid #475569;
    border-radius: 10px;
    background-color: #0F172A;
    font-size: 42px;
    font-weight: bold;
    color: #38BDF8;
}
QLineEdit#dataInput:focus {
    border-color: #38BDF8;
    background-color: #020617;
}

/* ========== 日志区 ========== */
QTextEdit#logText {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #E2E8F0;
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", "Courier New", monospace;
    font-size: 12pt;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* ========== QScrollBar 垂直滚动条 ========== */
QScrollBar:vertical {
    background-color: #0F172A;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #64748B;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

/* ========== QScrollBar 水平滚动条 ========== */
QScrollBar:horizontal {
    background-color: #0F172A;
    height: 10px;
    margin: 0;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #475569;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #64748B;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

/* ========== QToolTip ========== */
QToolTip {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Writer Tool")
