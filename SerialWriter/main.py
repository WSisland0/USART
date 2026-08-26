"""
Serial Writer Tool - USART 串口参数写入工具

入口模块，根据配置启动工业风、现代风或暗色风窗口。

用法：
    python main.py                   # 使用 config.json 中的风格设置
    python main.py --industrial      # 强制使用工业风
    python main.py --modern          # 强制使用现代风
    python main.py --dark            # 强制使用暗色风
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
from ui.dark_window import DarkWindow


def _resource_path(relative_path: str) -> str:
    """返回开发环境或 PyInstaller 单文件环境中的资源绝对路径。"""
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.abspath(__file__)),
    )
    return os.path.join(base_path, relative_path)


def _load_application_icon() -> QIcon:
    """加载窗口和任务栏共用的软件图标。"""
    return QIcon(_resource_path(os.path.join("assets", "serial_writer.ico")))


def main(force_style: str = None):
    """
    启动主窗口。

    参数:
        force_style: "industrial" | "modern" | "dark" | None。
                     传 None 时按 命令行 > exe文件名 > 配置文件 顺序确定风格。
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Serial Writer Tool")
    app.setOrganizationName("SerialWriter")
    app_icon = _load_application_icon()
    app.setWindowIcon(app_icon)

    config = load_config()

    # 确定风格（优先级: force_style > 命令行 > exe文件名 > 配置 > 默认 dark）
    style = config.get("style", "dark")
    if "--industrial" in sys.argv:
        style = "industrial"
    elif "--modern" in sys.argv:
        style = "modern"
    elif "--dark" in sys.argv:
        style = "dark"
    if force_style:
        style = force_style
    # PyInstaller 打包后，从 exe 文件名检测风格
    exe_name = os.path.basename(sys.executable).lower()
    if "工业风" in exe_name or "industrial" in exe_name:
        style = "industrial"
    elif "现代风" in exe_name or "modern" in exe_name:
        style = "modern"
    elif "暗色" in exe_name or "dark" in exe_name:
        style = "dark"

    if style == "industrial":
        window = IndustrialWindow()
    elif style == "modern":
        window = ModernWindow()
    else:
        window = DarkWindow()

    # 显式设置窗口图标，确保 Windows 标题栏和任务栏都能显示。
    window.setWindowIcon(app_icon)

    config["style"] = style
    save_config(config)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
