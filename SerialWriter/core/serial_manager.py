"""
串口管理模块 - 串口扫描、打开/关闭、数据收发、后台读取

使用 PySide6 QThread 在后台持续读取串口数据，
通过 Signal 将数据传递到 UI 层，避免阻塞主线程。

异常处理覆盖：
- 串口被占用
- 打开失败
- 发送失败
- 设备意外拔出
"""

from typing import Optional

import serial
import serial.tools.list_ports
from PySide6.QtCore import QObject, QThread, Signal, QMutex

from core.protocol import to_hex_string


class _ReadThread(QThread):
    """
    后台读取线程。

    持续从串口读取数据，将接收到的字节通过 Signal 发射出去。
    """

    # 收到数据信号 (bytes)
    data_received = Signal(bytes)
    # 发生错误信号 (错误描述)
    read_error = Signal(str)

    def __init__(self, ser: serial.Serial, parent=None):
        super().__init__(parent)
        self._serial = ser
        self._running = False
        self._mutex = QMutex()

    def run(self):
        """线程主循环，持续读取串口数据"""
        self._running = True
        while self._running:
            try:
                if self._serial is None or not self._serial.is_open:
                    break
                # wait_for_ready_read 等待数据到达，超时 0.5 秒
                available = self._serial.in_waiting
                if available > 0:
                    data = self._serial.read(available)
                    if data:
                        self.data_received.emit(data)
                else:
                    # 没有数据时短暂休眠，避免 CPU 空转
                    self.msleep(50)
            except serial.SerialException as e:
                self.read_error.emit(f"串口读取异常: {e}")
                break
            except OSError as e:
                self.read_error.emit(f"设备连接异常(可能已拔出): {e}")
                break

    def stop(self):
        """安全停止读取线程"""
        self._running = False
        self.wait(1000)  # 最多等待 1 秒


class SerialManager(QObject):
    """
    串口管理器。

    信号:
        data_received(bytes): 收到原始数据
        error_occurred(str): 发生错误
        port_opened(str): 串口已打开 (端口名)
        port_closed(str): 串口已关闭 (端口名)
    """

    data_received = Signal(bytes)
    error_occurred = Signal(str)
    port_opened = Signal(str)
    port_closed = Signal(str)

    # —— 校验位映射 ——
    _PARITY_MAP = {
        "None": serial.PARITY_NONE,
        "Even": serial.PARITY_EVEN,
        "Odd": serial.PARITY_ODD,
    }

    # —— 停止位映射 ——
    _STOPBITS_MAP = {
        "1": serial.STOPBITS_ONE,
        "1.5": serial.STOPBITS_ONE_POINT_FIVE,
        "2": serial.STOPBITS_TWO,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._serial: Optional[serial.Serial] = None
        self._read_thread: Optional[_ReadThread] = None

    @staticmethod
    def scan_ports() -> list[dict]:
        """
        扫描系统可用串口，返回设备名及描述信息。

        返回:
            列表，每项为 {"device": "COM3", "description": "USB-SERIAL CH340 (COM3)", "hwid": "USB VID:PID=1A86:7523"}
        """
        ports = serial.tools.list_ports.comports()
        result = []
        for p in sorted(ports, key=lambda p: p.device):
            result.append({
                "device": p.device,
                "description": p.description or "",
                "hwid": p.hwid or "",
            })
        return result

    def open(self, port: str, baud_rate: int, data_bits: int,
             parity: str, stop_bits: str) -> bool:
        """
        打开串口。

        参数:
            port:      端口号，如 "COM3"
            baud_rate: 波特率，如 9600
            data_bits: 数据位，5/6/7/8
            parity:    校验位，"None"/"Even"/"Odd"
            stop_bits: 停止位，"1"/"1.5"/"2"

        返回:
            成功返回 True，失败发射 error_occurred 信号并返回 False
        """
        # 如果已经打开，先关闭
        if self.is_open():
            self.close()

        try:
            self._serial = serial.Serial()
            self._serial.port = port
            self._serial.baudrate = baud_rate
            self._serial.bytesize = data_bits
            self._serial.parity = self._PARITY_MAP[parity]
            self._serial.stopbits = self._STOPBITS_MAP[stop_bits]
            self._serial.timeout = 0.1  # 读超时

            self._serial.open()

            # 启动后台读取线程
            self._read_thread = _ReadThread(self._serial)
            self._read_thread.data_received.connect(self._on_data_received)
            self._read_thread.read_error.connect(self._on_read_error)
            self._read_thread.start()

            self.port_opened.emit(port)
            return True

        except serial.SerialException as e:
            self._serial = None
            self.error_occurred.emit(f"打开串口失败 ({port}): {e}")
            return False
        except KeyError as e:
            self._serial = None
            self.error_occurred.emit(f"参数错误: 无效的 {e}")
            return False

    def close(self) -> bool:
        """
        关闭串口并停止读取线程。

        返回:
            成功返回 True
        """
        if self._read_thread is not None:
            self._read_thread.stop()
            self._read_thread = None

        port_name = ""
        if self._serial is not None:
            try:
                port_name = self._serial.port
                if self._serial.is_open:
                    self._serial.close()
            except serial.SerialException:
                pass
            self._serial = None

        self.port_closed.emit(port_name)
        return True

    def send(self, data: bytes) -> bool:
        """
        发送数据到串口。

        参数:
            data: 要发送的字节数据

        返回:
            发送成功返回 True，失败发射 error_occurred 并返回 False
        """
        if self._serial is None or not self._serial.is_open:
            self.error_occurred.emit("发送失败: 串口未打开")
            return False

        try:
            self._serial.write(data)
            self._serial.flush()
            return True
        except serial.SerialException as e:
            self.error_occurred.emit(f"发送失败: {e}")
            return False

    def is_open(self) -> bool:
        """检查串口是否已打开"""
        return self._serial is not None and self._serial.is_open

    # —— 内部槽函数 —— #

    def _on_data_received(self, data: bytes):
        """接收读取线程的数据，转发到外部"""
        self.data_received.emit(data)

    def _on_read_error(self, error_msg: str):
        """接收读取线程的错误，自动关闭串口并通知"""
        self.close()
        self.error_occurred.emit(error_msg)
