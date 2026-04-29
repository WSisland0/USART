"""
协议模块 - 数据帧构建与格式化

协议格式: FF FF [DATA] 00 FF
其中 DATA 为 1 字节 (0x00 ~ 0xFF)

以后协议可能改变，所以独立封装。
"""

# 帧定界常量
_FRAME_HEADER = b'\xFF\xFF'  # 帧头 2 字节
_FRAME_TAIL = b'\x00\xFF'    # 帧尾 2 字节

# DATA 在帧中的位置
DATA_BYTE_INDEX = 2  # DATA 字节在帧中的索引（0-based）


def build_frame(value: int) -> bytes:
    """
    根据输入值构建完整数据帧。

    参数:
        value: 0~255 的整数值

    返回:
        5 字节数据帧: FF FF [value] 00 FF

    异常:
        ValueError: 输入值超出 0~255 范围
    """
    if not (0 <= value <= 255):
        raise ValueError(f"数值 {value} 超出范围，必须在 0~255 之间")
    return _FRAME_HEADER + bytes([value]) + _FRAME_TAIL


def to_hex_string(data: bytes) -> str:
    """
    将字节数据转换为空格分隔的大写十六进制字符串。

    参数:
        data: 字节数据

    返回:
        例如: "FF FF 80 00 FF"
    """
    return ' '.join(f'{b:02X}' for b in data)


def get_data_byte(frame: bytes) -> int:
    """
    从帧中提取 DATA 字节。

    参数:
        frame: 完整数据帧

    返回:
        DATA 字节的整数值
    """
    if len(frame) > DATA_BYTE_INDEX:
        return frame[DATA_BYTE_INDEX]
    return 0
