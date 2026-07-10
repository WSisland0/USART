"""
协议模块 - 数据帧构建、CRC 校验和响应解析。

写入帧:
    A5 5A SEQ DigitalV CRC_L CRC_H

响应帧:
    A5 5A SEQ STATUS EmptyFre_L EmptyFre_H DigitalV CRC_L CRC_H

CRC 使用 CRC16/Modbus，低字节在前；校验范围不包含帧头和 CRC 本身。
"""

from dataclasses import dataclass


FRAME_HEADER = b"\xA5\x5A"
WRITE_FRAME_LEN = 6
RESPONSE_FRAME_LEN = 9
DATA_BYTE_INDEX = 3

STATUS_OK = 0x00
STATUS_EEPROM_WRITE_FAILED = 0x01
STATUS_EEPROM_READ_FAILED = 0x02
STATUS_EEPROM_CRC_FAILED = 0x03
STATUS_AD5245_WRITE_FAILED = 0x04
STATUS_FRAME_ERROR = 0x05

STATUS_MESSAGES = {
    STATUS_OK: "EEPROM OK",
    STATUS_EEPROM_WRITE_FAILED: "EEPROM WRITE FAILED",
    STATUS_EEPROM_READ_FAILED: "EEPROM READ FAILED",
    STATUS_EEPROM_CRC_FAILED: "EEPROM CRC FAILED",
    STATUS_AD5245_WRITE_FAILED: "AD5245 WRITE FAILED",
    STATUS_FRAME_ERROR: "FRAME ERROR",
}


@dataclass(frozen=True)
class DeviceResponse:
    """下位机响应帧解析结果。"""

    seq: int
    status: int
    empty_fre: int
    digital_v: int


def crc16_modbus(data: bytes) -> int:
    """计算 CRC16/Modbus，返回 0~0xFFFF。"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
            crc &= 0xFFFF
    return crc


def _append_crc(body: bytes) -> bytes:
    crc = crc16_modbus(body)
    return body + bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def build_frame(value: int, seq: int = 0) -> bytes:
    """
    根据输入值构建写入帧。

    参数:
        value: DigitalV，0~255。
        seq: 帧序号，0~255。

    返回:
        A5 5A SEQ DigitalV CRC_L CRC_H
    """
    if not (0 <= value <= 255):
        raise ValueError(f"数值 {value} 超出范围，必须在 0~255 之间")
    if not (0 <= seq <= 255):
        raise ValueError(f"序号 {seq} 超出范围，必须在 0~255 之间")

    body = bytes([seq, value])
    return FRAME_HEADER + _append_crc(body)


def to_hex_string(data: bytes) -> str:
    """将字节数据转换为空格分隔的大写十六进制字符串。"""
    return " ".join(f"{byte:02X}" for byte in data)


def get_data_byte(frame: bytes) -> int:
    """从写入帧中提取 DigitalV 字节。"""
    if len(frame) > DATA_BYTE_INDEX:
        return frame[DATA_BYTE_INDEX]
    return 0


def format_response(response: DeviceResponse) -> str:
    """格式化下位机响应，供日志显示。"""
    status_text = STATUS_MESSAGES.get(
        response.status,
        f"STATUS 0x{response.status:02X}",
    )
    return (
        f"{status_text}, "
        f"EmptyFre={response.empty_fre}, "
        f"DigitalV={response.digital_v}"
    )


class ResponseParser:
    """响应帧流式解析器，可处理分包、粘包和前导噪声。"""

    def __init__(self):
        self._buffer = bytearray()

    @property
    def has_pending_data(self) -> bool:
        """是否已经缓存了尚未组成完整响应帧的数据。"""
        return bool(self._buffer)

    def feed(self, data: bytes) -> list[DeviceResponse]:
        """输入串口收到的字节，返回解析出的 0 个或多个响应。"""
        responses: list[DeviceResponse] = []
        self._buffer.extend(data)

        while True:
            header_pos = self._buffer.find(FRAME_HEADER)
            if header_pos < 0:
                self._keep_possible_header_prefix()
                break

            if header_pos > 0:
                del self._buffer[:header_pos]

            if len(self._buffer) < RESPONSE_FRAME_LEN:
                break

            frame = bytes(self._buffer[:RESPONSE_FRAME_LEN])
            body = frame[2:7]
            expected_crc = crc16_modbus(body)
            received_crc = frame[7] | (frame[8] << 8)

            if received_crc != expected_crc:
                del self._buffer[0]
                continue

            seq = body[0]
            status = body[1]
            empty_fre = body[2] | (body[3] << 8)
            digital_v = body[4]
            responses.append(DeviceResponse(seq, status, empty_fre, digital_v))
            del self._buffer[:RESPONSE_FRAME_LEN]

        return responses

    def _keep_possible_header_prefix(self):
        if self._buffer.endswith(FRAME_HEADER[:1]):
            self._buffer[:] = FRAME_HEADER[:1]
        else:
            self._buffer.clear()
