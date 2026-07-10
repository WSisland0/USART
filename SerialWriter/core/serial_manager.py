"""
串口管理模块 - 串口扫描、打开/关闭、数据收发、后台读取

使用 PySide6 QThread 在后台持续读取串口数据，
通过 Signal 将数据传递到 UI 层，避免阻塞主线程。

串口打开操作也在工作线程中执行，避免 open() 调用阻塞 UI。

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

# —— 校验位映射 ——
_PARITY_MAP = {
    "None": serial.PARITY_NONE,
    "Even": serial.PARITY_EVEN,
    "Odd":  serial.PARITY_ODD,
}

# —— 停止位映射 ——
_STOPBITS_MAP = {
    "1":   serial.STOPBITS_ONE,
    "1.5": serial.STOPBITS_ONE_POINT_FIVE,
    "2":   serial.STOPBITS_TWO,
}


class _OpenWorker(QThread):
    """
    后台打开串口线程。

    打开串口是阻塞 I/O 操作（设备驱动协商），放在工作线程中
    执行可避免冻结 UI。完成后通过 Signal 将串口对象或错误传回。
    """

    opened = Signal(object)  # serial.Serial 对象
    failed = Signal(str)     # 错误描述

    def __init__(self, port: str, baud_rate: int, data_bits: int,
                 parity: str, stop_bits: str, parent=None):
        super().__init__(parent)
        self._port = port
        self._baud_rate = baud_rate
        self._data_bits = data_bits
        self._parity = parity
        self._stop_bits = stop_bits

    def run(self):
        try:
            ser = serial.Serial()
            ser.port = self._port
            ser.baudrate = self._baud_rate
            ser.bytesize = self._data_bits
            ser.parity = _PARITY_MAP[self._parity]
            ser.stopbits = _STOPBITS_MAP[self._stop_bits]
            ser.timeout = 0.1
            ser.write_timeout = 0.5  # write() 超时，防止虚拟串口阻塞
            ser.open()
            self.opened.emit(ser)
        except serial.SerialException as e:
            self.failed.emit(f"打开串口失败 ({self._port}): {e}")
        except KeyError as e:
            self.failed.emit(f"参数错误: 无效的 {e}")


class _SendWorker(QThread):
    """
    后台发送线程。

    write() 在虚拟串口（蓝牙/扩展坞）上可能阻塞，
    放在工作线程中执行可避免冻结 UI。
    """

    sent = Signal()          # 发送成功
    failed = Signal(str)     # 错误描述

    def __init__(self, ser: serial.Serial, data: bytes,
                 serial_mutex: QMutex, parent=None):
        super().__init__(parent)
        self._serial = ser
        self._data = data
        self._serial_mutex = serial_mutex

    def run(self):
        try:
            self._serial_mutex.lock()
            try:
                self._serial.write(self._data)
            finally:
                self._serial_mutex.unlock()
            self.sent.emit()
        except serial.SerialException as e:
            self.failed.emit(f"发送失败: {e}")


class _ReadThread(QThread):
    """
    后台读取线程。

    持续从串口读取数据，将接收到的字节通过 Signal 发射出去。
    """

    # 收到数据信号 (bytes)
    data_received = Signal(bytes)
    # 发生错误信号 (错误描述)
    read_error = Signal(str)

    def __init__(self, ser: serial.Serial, serial_mutex: QMutex, parent=None):
        super().__init__(parent)
        self._serial = ser
        self._serial_mutex = serial_mutex
        self._running = False

    def run(self):
        """线程主循环，持续读取串口数据"""
        self._running = True
        while self._running:
            try:
                if self._serial is None or not self._serial.is_open:
                    break
                # 加锁保护对串口对象的并发访问
                self._serial_mutex.lock()
                try:
                    available = self._serial.in_waiting
                    if available > 0:
                        data = self._serial.read(available)
                    else:
                        data = None
                finally:
                    self._serial_mutex.unlock()
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
        busy_changed(bool): 忙状态变化（正在打开串口时通知 UI 禁用按钮）
    """

    data_received = Signal(bytes)
    error_occurred = Signal(str)
    port_opened = Signal(str)
    port_closed = Signal(str)
    busy_changed = Signal(bool)
    send_done = Signal()  # 发送完成（成功或失败）

    def __init__(self, parent=None):
        super().__init__(parent)
        self._serial: Optional[serial.Serial] = None
        self._read_thread: Optional[_ReadThread] = None
        self._open_worker: Optional[_OpenWorker] = None
        self._send_worker: Optional[_SendWorker] = None
        self._busy = False
        self._serial_mutex = QMutex()  # 保护串口对象并发读写

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

    def _set_busy(self, busy: bool):
        """设置忙状态，变化时发射信号"""
        if self._busy != busy:
            self._busy = busy
            self.busy_changed.emit(busy)

    def is_busy(self) -> bool:
        """是否正在执行异步操作（打开中）"""
        return self._busy

    def open(self, port: str, baud_rate: int, data_bits: int,
             parity: str, stop_bits: str):
        """
        异步打开串口（不阻塞 UI）。

        参数:
            port:      端口号，如 "COM3"
            baud_rate: 波特率，如 9600
            data_bits: 数据位，5/6/7/8
            parity:    校验位，"None"/"Even"/"Odd"
            stop_bits: 停止位，"1"/"1.5"/"2"

        注:
            结果通过 port_opened / error_occurred 信号异步返回。
            可通过 is_busy() / busy_changed 检测操作是否完成。
        """
        # 防呆：正在打开中，忽略重复请求
        if self._busy:
            return

        # 如果已经打开，先关闭
        if self.is_open():
            self.close()

        self._set_busy(True)

        self._open_worker = _OpenWorker(
            port, baud_rate, data_bits, parity, stop_bits
        )
        self._open_worker.opened.connect(self._on_open_done)
        self._open_worker.failed.connect(self._on_open_failed)
        self._open_worker.start()

    def _on_open_done(self, ser: serial.Serial):
        """后台线程打开成功"""
        self._open_worker = None
        self._serial_mutex.lock()
        try:
            self._serial = ser
        finally:
            self._serial_mutex.unlock()

        # 启动后台读取线程
        self._read_thread = _ReadThread(self._serial, self._serial_mutex)
        self._read_thread.data_received.connect(self._on_data_received)
        self._read_thread.read_error.connect(self._on_read_error)
        self._read_thread.start()

        self._set_busy(False)
        self.port_opened.emit(ser.port)

    def _on_open_failed(self, error_msg: str):
        """后台线程打开失败"""
        self._open_worker = None
        self._serial_mutex.lock()
        try:
            self._serial = None
        finally:
            self._serial_mutex.unlock()
        self._set_busy(False)
        self.error_occurred.emit(error_msg)

    def close(self) -> bool:
        """
        关闭串口并停止读取线程。

        返回:
            成功返回 True
        """
        # 如果正在打开中，先等待打开线程完成再关闭
        if self._open_worker is not None and self._open_worker.isRunning():
            self._open_worker.opened.disconnect(self._on_open_done)
            self._open_worker.failed.disconnect(self._on_open_failed)
            self._open_worker.wait(2000)
            self._open_worker = None
            self._set_busy(False)

        # 取消正在进行的发送
        if self._send_worker is not None and self._send_worker.isRunning():
            self._send_worker.sent.disconnect(self._on_send_done)
            self._send_worker.failed.disconnect(self._on_send_failed)
            self._send_worker.wait(2000)
            self._send_worker = None

        if self._read_thread is not None:
            self._read_thread.stop()
            self._read_thread = None

        self._serial_mutex.lock()
        try:
            port_name = ""
            if self._serial is not None:
                try:
                    port_name = self._serial.port
                    if self._serial.is_open:
                        self._serial.close()
                except serial.SerialException:
                    pass
                self._serial = None
        finally:
            self._serial_mutex.unlock()

        self.port_closed.emit(port_name)
        return True

    def send(self, data: bytes):
        """
        异步发送数据到串口（不阻塞 UI）。

        参数:
            data: 要发送的字节数据

        注:
            结果通过 send_done / error_occurred 信号异步返回。
            串口未打开时同步发射 error_occurred 并立即返回。
        """
        if self._serial is None or not self._serial.is_open:
            self.error_occurred.emit("发送失败: 串口未打开")
            self.send_done.emit()
            return

        # 防呆：上一次发送还在进行中
        if self._send_worker is not None and self._send_worker.isRunning():
            return

        self._send_worker = _SendWorker(
            self._serial, data, self._serial_mutex
        )
        self._send_worker.sent.connect(self._on_send_done)
        self._send_worker.failed.connect(self._on_send_failed)
        self._send_worker.start()

    def _on_send_done(self):
        """后台发送成功"""
        self._send_worker = None
        self.send_done.emit()

    def _on_send_failed(self, error_msg: str):
        """后台发送失败"""
        self._send_worker = None
        self.error_occurred.emit(error_msg)
        self.send_done.emit()

    def is_open(self) -> bool:
        """检查串口是否已打开（线程安全）"""
        self._serial_mutex.lock()
        try:
            return self._serial is not None and self._serial.is_open
        finally:
            self._serial_mutex.unlock()

    # —— 内部槽函数 —— #

    def _on_data_received(self, data: bytes):
        """接收读取线程的数据，转发到外部"""
        if not data:
            return
        self.data_received.emit(data)

    def _on_read_error(self, error_msg: str):
        """接收读取线程的错误，自动关闭串口并通知"""
        self.close()
        self.error_occurred.emit(error_msg)
