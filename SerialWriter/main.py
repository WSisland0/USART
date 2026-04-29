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


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Serial Writer Tool")
    app.setOrganizationName("SerialWriter")

    # 加载配置
    config = load_config()

    # 命令行参数覆盖配置文件
    style = config.get("style", "modern")
    if "--industrial" in sys.argv:
        style = "industrial"
    elif "--modern" in sys.argv:
        style = "modern"

    # 根据风格创建对应窗口
    if style == "industrial":
        window = IndustrialWindow()
        print("[Main] 启动工业风窗口")
    else:
        window = ModernWindow()
        print("[Main] 启动现代风窗口")

    # 更新配置中的风格
    config["style"] = style
    save_config(config)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
