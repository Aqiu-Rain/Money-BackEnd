# 导入系统库

# 导入第三方库
from loguru import logger

# 导入自定义库

# 定义全局变量

# 从txt文件读取16进制数据，且以字节流输出
def read_serial_data_from_file(file_name: str) -> bytes:
    """从十六进制文本文件读取并转换（处理大端序字段）"""
    # 判断文件是否存在
    pass

    try:
        # 打开文件读取数据
        with open(file_name, 'r') as file:
            hex_pairs = file.read().split()  # 按空格分割每个字节
            return bytes.fromhex(''.join(hex_pairs))
            # return bytes.fromhex(file.read()) 
    except Exception as e:
        logger.error(f"failed to read data: {str(e)}")
        return b''
    
def save_to_file(data: bytes):
    with open("temp.bmp", "wb") as file:
        file.write(data)