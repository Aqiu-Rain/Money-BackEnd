# 导入系统库
from loguru import logger
import time

# 导入第三方库
import serial
import serial.tools
import serial.tools.list_ports_windows
# import serial.tools.list_ports_posix

# 导入自定义库
from app.services.serial.serial_model import SerialParameters

# 定义串口通信类
class SerialCommunication:
    def __init__(self):
        """初始化串口通信参数"""
        self.serial_parameters = None  # 串口通信参数
        self.serial_conn = serial.Serial()  # 串口连接对象

    def set_serial_parm(self, serial_param: SerialParameters):
        if serial_param:
            self.serial_parameters = serial_param

    def open_connection(self) -> bool:
        """打开串口连接"""
        try:
            # 设置串口通信参数
            self.serial_conn.port = self.serial_parameters.port
            self.serial_conn.baudrate = self.serial_parameters.baudrate
            self.serial_conn.bytesize = self.serial_parameters.bytesize
            self.serial_conn.parity = self.serial_parameters.parity
            self.serial_conn.stopbits = self.serial_parameters.stopbits
            self.serial_conn.timeout = self.serial_parameters.timeout
            self.serial_conn.xonxoff = self.serial_parameters.xonxoff
            self.serial_conn.rtscts = self.serial_parameters.rtscts
            self.serial_conn.dsrdtr = self.serial_parameters.dsrdtr
            self.serial_conn.rts = False
            self.serial_conn.dtr = False

            # 打开串口连接
            self.serial_conn.open()
            return self.serial_conn.is_open
        
        except serial.SerialException as e:
            logger.error(f"open connection failed: {self.serial_parameters.port}: {str(e)}")
            return False

    def close_connection(self):
        """关闭串口连接"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.serial_conn = None

    def send_data(self, data: str) -> bool:
        """发送数据到串口"""
        # 检查串口是否连接
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.warning(f"send data failed: serial don't connect")
            return False

        # 开始发送数据
        try:
            self.serial_conn.write(data.encode())
            self.serial_conn.flush()  # 等待数据发送完成
            return True
        except serial.SerialTimeoutException:
            logger.warning(f"send data failed: timeout")
        except serial.SerialException as e:
            logger.error(f"send data failed: {str(e)}")
        return False

    def receive_data(self, data_length) -> bytes:
        """接收串口数据"""
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("receive data filed: serial don't connect")
            raise Exception("error")
            return None

        buffer = bytearray()
        start_time = time.time()
        
        while len(buffer) < data_length:
            try:
                # 非阻塞读取，每次最多读取剩余所需长度
                remaining = data_length - len(buffer)
                chunk = self.serial_conn.read(min(remaining, 1656))  # 优化读取效率
                
                if not chunk:
                    # 超时无数据，检查连接状态
                    if not self.serial_conn.is_open:
                        logger.error("Serial port closed unexpectedly")
                        raise serial.SerialException("Port closed during read")
                
                buffer.extend(chunk)
                logger.info(f"Received {len(chunk)} bytes, total {len(buffer)}/{data_length}")
                
                # 提前终止条件：已读够长度或超时累积
                if len(buffer) >= data_length:
                    break
            except serial.SerialException as e:
                logger.error(f"Read error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
            
        return buffer[:data_length] if len(buffer) >= data_length else None


    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.serial_conn and self.serial_conn.is_open


def get_ports():
    port_data = serial.tools.list_ports_windows.comports()
    for port, desc, hwid in sorted(port_data):
        logger.info(f"Port:{port}, Desc:{desc}, Hwid:{hwid}")

    connnected_ports = [{"Port":port, "Desc":desc} for (port, desc, hwid) in sorted(port_data)]
    logger.info(f"connnected ports: {str(connnected_ports)}")
    return connnected_ports
