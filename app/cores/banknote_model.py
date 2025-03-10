from typing import NewType
from dataclasses import dataclass
from datetime import date

# 定义类型别名增强可读性
UInt16 = NewType('UInt16', int)
UInt32 = NewType('UInt32', int)
Int16 = NewType('Int16', int)

# 币种映射表
CURRENCY_MAP = {
    'USD': '美元', 'EUR': '欧元', 'GBP': '英镑',
    'CNY': '人民币', 'JPY': '日元', 'AUD': '澳元',
    'HKD': '港元', 'TL': '新里拉', 'CAD': '加元',
    'RUB': '卢布', 'KRW': '韩元'
}

@dataclass
class TImageSNo:
    undefine: list[Int16]  # 4个Int16（协议明确要求）
    sno: bytes             # 1536字节原始数据（协议中的UInt8数组）

@dataclass
class BanknoteInfo:
    date: UInt16                  # 日期（协议位置8-9）
    time: UInt16                  # 时间（位置10-11）
    tf_flag: UInt16               # 真伪标志（位置12-13）
    valuta: UInt32                # 币值（位置14-17）
    fsn_count: UInt16             # 纸币计数（位置18-19）
    money_flag: list[UInt16]      # 货币标志[4]（位置20-27）
    ver: UInt16                   # 版本号（位置28-29）
    undefine: UInt16              # 未定义字段（位置30-31）
    char_num: UInt16              # 冠字号码字符数（位置32-33）
    sno: list[UInt16]             # 冠字号码[12]（位置34-57）
    machine_number: list[UInt16]  # 机具编号[24]（位置58-105）
    reserve1: UInt16              # 保留字（位置106-107）
    image_sno: TImageSNo          # 图像数据（位置108-1643）

    @property
    def parsed_date(self) -> date:
        """解析日期字段（UInt16）为实际日期"""
        # 协议公式：Date = ((Year-1980)<<9) + (Month<<5) + Day
        encoded = self.date
        year = (encoded >> 9) + 1980
        month = (encoded >> 5) & 0b1111
        day = encoded & 0b11111
        return date(year, month, day)
    
    @property
    def parsed_time(self) -> tuple[int, int, int]:
        """解析时间字段（UInt16）为时分秒"""
        # 协议公式：Time = (Hour<<11) + (Minute<<5) + Second//2
        encoded = self.time
        hour = encoded >> 11
        minute = (encoded >> 5) & 0b111111
        second = (encoded & 0b11111) * 2
        return (hour, minute, second)

    @property
    def currency_code(self) -> str:
        """解析币种标志为3-4位字母代码"""
        # 将UInt16列表转换为ASCII字符（过滤零值）
        chars = [chr(c) for c in self.money_flag if c != 0]
        return ''.join(chars).strip().upper()

    @property
    def parsed_currency(self) -> str:
        """获取币种中文名称"""
        code = self.currency_code
        return CURRENCY_MAP.get(code, f"未知币种({code})")

    def __post_init__(self):
        # 验证币种标志
        valid_chars = set(chr(c) for c in range(65, 91))  # A-Z
        for c in self.currency_code:
            if c not in valid_chars:
                raise ValueError(f"无效币种字符: {c}") 