from dataclasses import dataclass
from enum import Enum

class Bytesize(Enum):
    """数据位枚举"""
    FIVEBITS = 5
    SIXBITS = 6
    SEVENBITS = 7
    EIGHTBITS = 8

class Parity(Enum):
    """校验位枚举"""
    NONE = 'N'
    EVEN = 'E'
    ODD = 'O'
    MARK = 'M'
    SPACE = 'S'

class Stopbits(Enum):
    """停止位枚举"""
    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2

@dataclass
class SerialParameters:
    """串口通信参数数据对象"""
    port: str
    baudrate: int = 9600
    bytesize: int = Bytesize.EIGHTBITS
    parity: str = Parity.NONE
    stopbits: int = Stopbits.ONE
    timeout: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False
