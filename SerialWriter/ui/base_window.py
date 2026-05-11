"""
主窗口基类 - 包含所有共享布局和业务逻辑

区域布局（从上到下）：
  区域1：串口设置
  区域2：数据设置（主体）
  区域3：帧展示区（只读）
  区域4：日志区

工业风和现代风窗口继承此类，仅覆盖 _get_stylesheet() 提供不同的 QSS。
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QComboBox, QPushButton, QLineEdit, QTextEdit,
    QMessageBox, QFileDialog, QMenu, QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIntValidator, QTextCursor, QAction

from core.serial_manager import SerialManager
from core.protocol import build_frame, to_hex_string, get_data_byte
from core.logger import LogManager, LogCategory, LogEntry
from core.config_manager import load_config, save_config

# ———————— 默认输入值 ————————
_DEFAULT_DATA_VALUE = 128


def _bytes_to_hex_str(data: bytes) -> str:
    """将字节数据格式化为空格分隔的大写十六进制"""
    return ' '.join(f'{b:02X}' for b in data)


def _bytes_to_ascii_str(data: bytes) -> str:
    """将字节数据转换为可读 ASCII 字符串，不可打印字符替换为 ."""
    result = []
    for b in data:
        if 32 <= b <= 126:
            result.append(chr(b))
        else:
            result.append('.')
    return ''.join(result)


class BaseWindow(QMainWindow):
    """主窗口基类"""

    # 子类可覆盖此字典以适配不同主题的日志颜色
    _log_colors = {
        LogCategory.TX:    "#1976D2",  # 蓝色
        LogCategory.RX:    "#388E3C",  # 绿色
        LogCategory.ERROR: "#D32F2F",  # 红色
        LogCategory.INFO:  "#757575",  # 灰色
    }

    def __init__(self):
        super().__init__()

        # ———————— 核心组件 ————————
        self._serial_mgr = SerialManager(self)
        self._log_mgr = LogManager(self)
        self._config = load_config()

        # 上次发送的值（用于参考）
        self._last_sent_value = _DEFAULT_DATA_VALUE

        # ———————— 窗口基本设置 ————————
        self.setWindowTitle("Serial Writer Tool")
        self.resize(900, 700)
        self.setMinimumSize(640, 500)

        # 应用样式表（子类提供）
        self.setStyleSheet(self._get_stylesheet())

        # 构建 UI
        self._setup_menu()
        self._setup_ui()
        self._connect_signals()

        # 恢复配置
        self._restore_config()

        # 初始帧显示
        self._update_frame_display()

    # ===================== 子类覆盖 =====================

    def _get_stylesheet(self) -> str:
        """子类覆盖此方法返回 QSS 样式表"""
        return ""

    # ===================== 菜单栏 =====================

    def _setup_menu(self):
        menubar = self.menuBar()

        # —— 文件菜单 ——
        file_menu = menubar.addMenu("文件(&F)")

        save_log_act = QAction("保存日志(&S)", self)
        save_log_act.triggered.connect(self._save_log)
        file_menu.addAction(save_log_act)

        file_menu.addSeparator()

        exit_act = QAction("退出(&Q)", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # —— 帮助菜单 ——
        help_menu = menubar.addMenu("帮助(&H)")
        about_act = QAction("关于(&A)", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    # ===================== UI 构建 =====================

    def _setup_ui(self):
        """搭建完整界面"""
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(12, 8, 12, 8)

        # 区域1：串口设置
        root.addWidget(self._create_serial_settings())

        # 区域2：数据设置（主体，占用弹性空间）
        root.addWidget(self._create_data_settings(), 1)

        # 区域3：帧展示区
        root.addWidget(self._create_frame_display())

        # 区域4：日志区
        root.addWidget(self._create_log_area(), 1)

    # ---------- 区域1：串口设置 ----------

    def _create_serial_settings(self) -> QGroupBox:
        group = QGroupBox("串口设置")
        grid = QGridLayout(group)
        grid.setSpacing(8)

        # 端口号
        grid.addWidget(QLabel("端口号:"), 0, 0)
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(100)
        grid.addWidget(self._port_combo, 0, 1)
        self._btn_refresh = QPushButton("刷新")
        self._btn_refresh.setFixedWidth(60)
        grid.addWidget(self._btn_refresh, 0, 2)

        # 波特率
        grid.addWidget(QLabel("波特率:"), 0, 3)
        self._baud_combo = QComboBox()
        self._baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self._baud_combo.setCurrentText("9600")
        grid.addWidget(self._baud_combo, 0, 4)

        # 数据位
        grid.addWidget(QLabel("数据位:"), 1, 0)
        self._data_bits_combo = QComboBox()
        self._data_bits_combo.addItems(["5", "6", "7", "8"])
        self._data_bits_combo.setCurrentText("8")
        grid.addWidget(self._data_bits_combo, 1, 1)

        # 校验位
        grid.addWidget(QLabel("校验位:"), 1, 2)
        self._parity_combo = QComboBox()
        self._parity_combo.addItems(["None", "Even", "Odd"])
        grid.addWidget(self._parity_combo, 1, 3)

        # 停止位
        grid.addWidget(QLabel("停止位:"), 1, 4)
        self._stop_bits_combo = QComboBox()
        self._stop_bits_combo.addItems(["1", "1.5", "2"])
        grid.addWidget(self._stop_bits_combo, 1, 5)

        # 打开/关闭 + 状态
        btn_row = QHBoxLayout()
        self._btn_open = QPushButton("打开串口")
        self._btn_open.setObjectName("btnOpen")
        self._btn_close = QPushButton("关闭串口")
        self._btn_close.setObjectName("btnClose")
        self._btn_close.setEnabled(False)
        self._status_label = QLabel('● <span style="color:#9E9E9E;">未连接</span>')
        self._status_label.setMinimumWidth(160)

        btn_row.addWidget(self._btn_open)
        btn_row.addWidget(self._btn_close)
        btn_row.addSpacing(20)
        btn_row.addWidget(self._status_label)
        btn_row.addStretch()

        grid.addLayout(btn_row, 2, 0, 1, 6)

        # 接收显示模式
        grid.addWidget(QLabel("接收显示:"), 0, 5)
        self._receive_mode_combo = QComboBox()
        self._receive_mode_combo.addItems(["HEX", "ASCII"])
        grid.addWidget(self._receive_mode_combo, 0, 6)

        return group

    # ---------- 区域2：数据设置 ----------

    def _create_data_settings(self) -> QGroupBox:
        group = QGroupBox("数据设置")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # 中央大输入框
        self._data_input = QLineEdit()
        self._data_input.setAlignment(Qt.AlignCenter)
        self._data_input.setPlaceholderText("输入 0~255")
        # 大字号在样式表中设置
        font = QFont()
        font.setPointSize(42)
        self._data_input.setFont(font)
        self._data_input.setValidator(QIntValidator(0, 255))
        self._data_input.setText(str(_DEFAULT_DATA_VALUE))
        self._data_input.setObjectName("dataInput")
        layout.addWidget(self._data_input)

        # 微调按钮行 [-10] [-5] [-1] [+1] [+5] [+10]
        step_row = QHBoxLayout()
        step_row.setSpacing(8)
        step_row.addStretch()

        steps = [-10, -5, -1, 1, 5, 10]
        for s in steps:
            prefix = "" if s < 0 else "+"
            label = f"{prefix}{s}"
            btn = QPushButton(label)
            btn.setObjectName("stepBtn")
            btn.clicked.connect(lambda checked, amount=s: self._on_step(amount))
            step_row.addWidget(btn)
            if s == -1:
                # 在 -1 和 +1 之间加些间距
                step_row.addSpacing(30)

        step_row.addStretch()
        layout.addLayout(step_row)

        # 大发送按钮
        self._btn_send = QPushButton("发  送")
        self._btn_send.setObjectName("btnSend")
        self._btn_send.setMinimumHeight(50)
        font_send = QFont()
        font_send.setPointSize(18)
        font_send.setBold(True)
        self._btn_send.setFont(font_send)
        layout.addWidget(self._btn_send)

        return group

    # ---------- 区域3：帧展示区 ----------

    def _create_frame_display(self) -> QGroupBox:
        group = QGroupBox("帧预览")
        layout = QHBoxLayout(group)

        self._frame_label = QLabel()
        font = QFont("Consolas, Courier New, monospace")
        font.setPointSize(16)
        font.setBold(True)
        self._frame_label.setFont(font)
        self._frame_label.setAlignment(Qt.AlignCenter)
        self._frame_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._frame_label)

        return group

    # ---------- 区域4：日志区 ----------

    def _create_log_area(self) -> QGroupBox:
        group = QGroupBox("通信日志")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        # 日志文本框（只读）
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setObjectName("logText")
        font = QFont("Consolas, Courier New, monospace")
        font.setPointSize(10)
        self._log_text.setFont(font)
        layout.addWidget(self._log_text, 1)

        # 底部按钮
        btn_row = QHBoxLayout()
        self._btn_clear_log = QPushButton("清空日志")
        self._btn_save_log = QPushButton("保存日志")
        btn_row.addWidget(self._btn_clear_log)
        btn_row.addWidget(self._btn_save_log)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return group

    # ===================== 信号连接 =====================

    def _connect_signals(self):
        """连接所有信号和槽"""

        # —— 串口管理器信号 ——
        self._serial_mgr.data_received.connect(self._on_data_received)
        self._serial_mgr.error_occurred.connect(self._on_serial_error)
        self._serial_mgr.port_opened.connect(self._on_port_opened)
        self._serial_mgr.port_closed.connect(self._on_port_closed)
        self._serial_mgr.busy_changed.connect(self._on_serial_busy_changed)
        self._serial_mgr.send_done.connect(self._on_send_done)

        # —— 按钮 ——
        self._btn_refresh.clicked.connect(self._on_refresh_ports)
        self._btn_open.clicked.connect(self._on_open_port)
        self._btn_close.clicked.connect(self._on_close_port)
        self._btn_send.clicked.connect(self._on_send)
        self._btn_clear_log.clicked.connect(self._log_mgr.clear)
        self._btn_save_log.clicked.connect(self._save_log)

        # —— 输入值变化 → 更新帧显示 ——
        self._data_input.textEdited.connect(self._update_frame_display)
        self._data_input.editingFinished.connect(self._clamp_input_value)

        # —— 接收模式切换 ——
        self._receive_mode_combo.currentTextChanged.connect(self._on_receive_mode_changed)

        # —— 日志信号 ——
        self._log_mgr.entry_added.connect(self._on_log_entry)
        self._log_mgr.cleared.connect(self._log_text.clear)

    # ===================== 配置恢复 =====================

    def _restore_config(self):
        """从配置文件恢复上次设置"""
        cfg = self._config

        # 串口参数
        self._baud_combo.setCurrentText(str(cfg.get("baud_rate", 9600)))
        self._data_bits_combo.setCurrentText(str(cfg.get("data_bits", 8)))
        self._parity_combo.setCurrentText(cfg.get("parity", "None"))
        self._stop_bits_combo.setCurrentText(str(cfg.get("stop_bits", 1)))

        # 接收模式
        mode = cfg.get("receive_mode", "hex")
        self._receive_mode_combo.setCurrentText(mode.upper())

        # 刷新端口列表，并选中上次使用的端口
        self._on_refresh_ports()
        saved_port = cfg.get("port", "")
        if saved_port:
            idx = self._port_combo.findData(saved_port)
            if idx >= 0:
                self._port_combo.setCurrentIndex(idx)

    # ===================== 槽函数 =====================

    def _on_refresh_ports(self):
        """刷新可用串口列表"""
        current = self._port_combo.currentData()
        self._port_combo.clear()
        ports = SerialManager.scan_ports()
        if ports:
            for p in ports:
                # 显示: "COM3 - USB-SERIAL CH340 (COM3)"，设备名存为 userData
                if p.get("description"):
                    display = f"{p['device']} - {p['description']}"
                else:
                    display = p["device"]
                self._port_combo.addItem(display, p["device"])
            idx = self._port_combo.findData(current)
            if idx >= 0:
                self._port_combo.setCurrentIndex(idx)
        else:
            self._port_combo.addItem("(无可用串口)", "")
        self._log_mgr.add_info(f"扫描到 {len(ports)} 个串口")

    def _on_open_port(self):
        """打开串口（异步，不阻塞 UI）"""
        port = self._port_combo.currentData()
        if not port:
            QMessageBox.warning(self, "提示", "请先选择有效的串口")
            return

        # 防呆：正在打开中，忽略重复点击
        if self._serial_mgr.is_busy():
            return

        baud = int(self._baud_combo.currentText())
        data_bits = int(self._data_bits_combo.currentText())
        parity = self._parity_combo.currentText()
        stop_bits = self._stop_bits_combo.currentText()

        # 异步打开，结果通过 port_opened / error_occurred 信号返回
        self._serial_mgr.open(port, baud, data_bits, parity, stop_bits)
        self._log_mgr.add_info(f"正在打开串口 {port}...")

    def _on_close_port(self):
        """关闭串口"""
        self._serial_mgr.close()
        self._log_mgr.add_info("串口已关闭")

    def _on_serial_busy_changed(self, busy: bool):
        """串口管理器忙状态变化，禁用/启用相关控件"""
        self._btn_open.setEnabled(not busy)
        self._btn_close.setEnabled(False if busy else self._serial_mgr.is_open())
        self._port_combo.setEnabled(not busy)
        self._btn_refresh.setEnabled(not busy)
        self._btn_send.setEnabled(not busy)
        if busy:
            self._status_label.setText(
                '<span style="color:#F57C00;">⏳ 正在打开...</span>'
            )

    def _on_port_opened(self, port: str):
        """串口打开成功的回调"""
        self._status_label.setText(
            '<span style="color:#388E3C;font-weight:bold;">● 已连接</span>'
        )
        self._btn_open.setEnabled(False)
        self._btn_close.setEnabled(True)
        self._port_combo.setEnabled(False)
        self._btn_refresh.setEnabled(True)
        self._btn_send.setEnabled(True)
        self._log_mgr.add_info(f"串口 {port} 已打开")

    def _on_port_closed(self, port: str):
        """串口关闭的回调"""
        if self._serial_mgr.is_busy():
            return  # 正在打开中，不更新状态
        self._status_label.setText(
            '<span style="color:#9E9E9E;">● 未连接</span>'
        )
        self._btn_open.setEnabled(True)
        self._btn_close.setEnabled(False)
        self._port_combo.setEnabled(True)
        self._btn_refresh.setEnabled(True)
        self._btn_send.setEnabled(True)

    def _on_send(self):
        """发送数据帧（异步，不阻塞 UI）"""
        if not self._serial_mgr.is_open():
            QMessageBox.warning(self, "提示", "请先打开串口再发送")
            return

        # 获取当前值并构建帧
        try:
            value = int(self._data_input.text())
        except ValueError:
            QMessageBox.warning(self, "提示", "请输入有效的数值 (0~255)")
            return

        try:
            frame = build_frame(value)
        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
            return

        # 异步发送，结果由 send_done 信号通知
        self._serial_mgr.send(frame)
        hex_str = to_hex_string(frame)
        self._log_mgr.add_tx(hex_str)
        self._last_sent_value = value
        self._save_current_config()

    def _on_send_done(self):
        """发送完成（成功或失败），可用于恢复按钮状态等"""
        pass  # 预留扩展

    def _on_step(self, amount: int):
        """微调数值（不发送）"""
        try:
            current = int(self._data_input.text())
        except ValueError:
            current = 0
        new_val = max(0, min(255, current + amount))
        self._data_input.setText(str(new_val))
        self._update_frame_display()

    def _update_frame_display(self):
        """根据当前输入更新帧预览"""
        try:
            value = int(self._data_input.text())
        except ValueError:
            value = 0

        try:
            frame = build_frame(value)
        except ValueError:
            return

        # 构建 HTML，DATA 字节高亮
        hex_str = to_hex_string(frame)
        parts = hex_str.split(' ')
        # 帧格式: FF FF [DATA] 00 FF
        # parts[0]=FF, parts[1]=FF, parts[2]=DATA, parts[3]=00, parts[4]=FF
        if len(parts) == 5:
            html = (
                f'{parts[0]} {parts[1]} '
                f'<span style="color:#E65100;background:#FFF3E0;padding:2px 4px;">'
                f'[{parts[2]}]</span>'
                f' {parts[3]} {parts[4]}'
            )
        else:
            html = hex_str
        self._frame_label.setText(html)

    def _clamp_input_value(self):
        """输入框失去焦点时，确保值在 0~255 范围内"""
        try:
            val = int(self._data_input.text())
        except ValueError:
            val = _DEFAULT_DATA_VALUE
        val = max(0, min(255, val))
        self._data_input.setText(str(val))
        self._update_frame_display()

    def _on_data_received(self, data: bytes):
        """接收到串口数据"""
        mode = self._receive_mode_combo.currentText()
        if mode == "HEX":
            display = _bytes_to_hex_str(data)
        else:
            display = _bytes_to_ascii_str(data)
        self._log_mgr.add_rx(display)

    def _on_serial_error(self, error_msg: str):
        """串口错误"""
        self._log_mgr.add_error(error_msg)
        # 错误时恢复 UI 状态（busy_changed 已由 SerialManager._on_open_failed 触发）
        self._status_label.setText(
            '<span style="color:#9E9E9E;">● 未连接</span>'
        )
        self._btn_open.setEnabled(True)
        self._btn_close.setEnabled(False)
        self._port_combo.setEnabled(True)
        self._btn_refresh.setEnabled(True)
        self._btn_send.setEnabled(True)

    def _on_receive_mode_changed(self, mode: str):
        """接收显示模式切换"""
        self._log_mgr.add_info(f"接收显示模式切换为: {mode}")
        self._config["receive_mode"] = mode.lower()
        save_config(self._config)

    def _on_log_entry(self, entry: LogEntry):
        """新日志条目的 UI 更新"""
        color = self._log_colors.get(entry.category, "#333333")
        html = (
            f'<span style="color:{color};white-space:pre;">'
            f'{entry.formatted()}'
            f'</span><br>'
        )
        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html)
        # 自动滚动到底部
        self._log_text.setTextCursor(cursor)
        self._log_text.ensureCursorVisible()

    # ===================== 辅助功能 =====================

    def _save_log(self):
        """保存日志到文件"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "serial_log.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        if filepath:
            ok = self._log_mgr.save_to_file(filepath)
            if ok:
                self._log_mgr.add_info(f"日志已保存到: {filepath}")
            else:
                QMessageBox.critical(self, "错误", "保存日志失败")

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "<h3>Serial Writer Tool</h3>"
            "<p>USART 串口参数写入工具</p>"
            "<p>协议格式: FF FF [DATA] 00 FF<br>"
            "DATA 范围: 0~255 (十进制)</p>"
            ##"<p>Python 3.12 + PySide6 + pyserial</p>"
        )

    def _save_current_config(self):
        """保存当前界面配置到文件"""
        self._config["port"] = self._port_combo.currentData()
        self._config["baud_rate"] = int(self._baud_combo.currentText())
        self._config["data_bits"] = int(self._data_bits_combo.currentText())
        self._config["parity"] = self._parity_combo.currentText()
        self._config["stop_bits_str"] = self._stop_bits_combo.currentText()
        # stop_bits 存储为 float 或 int
        sb = self._stop_bits_combo.currentText()
        self._config["stop_bits"] = float(sb) if '.' in sb else int(sb)
        self._config["receive_mode"] = self._receive_mode_combo.currentText().lower()
        save_config(self._config)

    def closeEvent(self, event):
        """窗口关闭时清理资源并保存配置"""
        self._save_current_config()
        if self._serial_mgr.is_open():
            self._serial_mgr.close()
        event.accept()
