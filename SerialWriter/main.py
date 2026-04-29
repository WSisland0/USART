"""
Serial Writer Tool - USART 串口参数写入工具

入口模块，根据配置启动工业风或现代风窗口。

用法：
    python main.py                   # 使用 config.json 中的风格设置
    python main.py --industrial      # 强制使用工业风
    python main.py --modern          # 强制使用现代风
"""

import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from core.config_manager import load_config, save_config
from ui.industrial_window import IndustrialWindow
from ui.modern_window import ModernWindow


def main(force_style: str = None):
    """
    启动主窗口。

    参数:
        force_style: "industrial" | "modern" | None。
                     传 None 时按 命令行 > exe文件名 > 配置文件 顺序确定风格。
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Serial Writer Tool")
    app.setOrganizationName("SerialWriter")

    config = load_config()

    # 确定风格（优先级: force_style > 命令行 > exe文件名 > 配置 > 默认 modern）
    style = config.get("style", "modern")
    if "--industrial" in sys.argv:
        style = "industrial"
    elif "--modern" in sys.argv:
        style = "modern"
    if force_style:
        style = force_style
    # PyInstaller 打包后，从 exe 文件名检测风格
    exe_name = os.path.basename(sys.executable).lower()
    if "工业风" in exe_name or "industrial" in exe_name:
        style = "industrial"
    elif "现代风" in exe_name or "modern" in exe_name:
        style = "modern"

    if style == "industrial":
        window = IndustrialWindow()
    else:
        window = ModernWindow()

    config["style"] = style
    save_config(config)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
