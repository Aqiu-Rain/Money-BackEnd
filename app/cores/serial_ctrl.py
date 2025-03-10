# 导入系统库
from loguru import logger
import json
import struct
from dataclasses import asdict
import os
import sys
import re
from datetime import datetime

# 导入第三方库
from multiprocessing import Queue
from sqlalchemy.orm import Session

# 导入自定义库
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.services.serial.serial_communication import SerialCommunication
from app.services.serial.serial_model import SerialParameters
from app.cores.banknote_model import BanknoteInfo, TImageSNo
from app.services.image.image_saver import ImageSaverService, add_bmp_headers
from app.services.file.file_opt import read_serial_data_from_file, save_to_file
from app.models import Result
from app.utils.common import convert_to_datetime

# 定义全局变量
message_queue = Queue()
# 定义常量
MSG_LENGTH = 1650

# 定义串口控制器类
class SerialController:
    '''
    功能：
        1. 设置串口参数
        2. 打开串口
        3. 接受数据并推送给前端
            1. 数据解包
        4. 将数据存入数据库
    '''
    def __init__(self, db: Session, data_source: str = 'real'):
        self.db = db
        self.serial_communication = SerialCommunication()
        self.image_opt = ImageSaverService()
        self.database = None
        self.data_source = data_source # real代表数据是真实数据，test代表数据是从文件中读取的测试数据
        # 初始化数据
        self.msg_length = 0
        self.message = {}
        self.money_info = None

    # 设置串口参数
    def set_serial_param(self, serial_param: dict):
        '''
        serial_param: json类型
        '''
        # 解析json为字典
        param_dict = serial_param
        
        # 实例参数模型
        self.serial_communication.set_serial_parm(SerialParameters(**param_dict))

    # 打开串口
    def open_connection(self) -> bool:
        if not self.serial_communication.is_connected():
            return self.serial_communication.open_connection()
        
    # 关闭串口
    def close_connection(self):
        if self.serial_communication.is_connected():
            self.serial_communication.close_connection()
        
    # 数据接收及入库
    def recv_and_save_data(self):
        try:
            while True:
                # 接收数据
                if not self.recv_data():
                    logger.warning(f"recv data failed: data is not correct")
                    continue

                # 推送数据
                if not self.push_data():
                    logger.warning(f"push data failed: data is not correct")
                    continue

                # 数据入库
                if not self.save_data():
                    logger.warning(f"save data failed: data is not correct")
                    logger.warning(f"data is {self.message}")
                    continue
        except Exception as e:
            msg = f"recv data failed: {str(e)}"
            logger.error(msg)
            self.push_error(msg, "error")
            self.close_connection()
            return

    # 接收数据
    def recv_data(self) -> bool:
        # 接受包头
        while not self.recv_header():
            pass

        # 接受数据长度
        if not self.recv_data_length():
            logger.warning("recv data length failed: data length is not correct")
            return False

        # 接收核心数据（包含模式+纸币信息+包尾）
        if not self.recv_money_data():
            logger.warning("recv core data failed: core data is not correct")
            return False

        return True

            
    # 接收包头
    def recv_header(self) -> bool:
        data = self.serial_communication.receive_data(4)
        if data is None:
            return False
        
        if data == b'\xAE\xAE\xAE\xAE':
            return True
        else:
            msg = f"recv header failed: header is not correct {data}"
            logger.warning(msg)
            self.push_error(msg)
            self.serial_communication.clean_data()
            return False

    # 接收数据长度
    def recv_data_length(self) -> bool:
        data = self.serial_communication.receive_data(2)
        if data is None:
            return False

        # 解析消息长度（2字节）
        self.msg_length = struct.unpack('<H', data)[0]
        if self.msg_length == MSG_LENGTH:
            return True
        else:
            msg = f"recv data length failed: data length is not correct {self.msg_length}"
            logger.warning(msg)
            self.push_error(msg)
            return False

    # 接收纸币数据
    def recv_money_data(self) -> bool:
        try:
            data = self.serial_communication.receive_data(self.msg_length)
            if data is None:
                return False

            # 解析模式标志（2字节0X0001）
            mode_flag = struct.unpack('<H', data[:2])[0]
            if mode_flag != 0x0001:
                msg = f"recv mode flag failed: mode flag is not correct {mode_flag}"
                logger.warning(msg)
                self.push_error(msg)
                return False

            # 解析纸币信息（1644字节）
            money_data = data[2:-4]
            fmt = '<HHHIH4HHHH12H24HH4H1536s'  # 总长度=2+2+2+4+2+8+2+2+2+24+48+2+8+1536=1644
            fields = struct.unpack(fmt, money_data)
            self.money_info = BanknoteInfo(
                date=fields[0],
                time=fields[1],
                tf_flag=fields[2],
                valuta=fields[3],
                fsn_count=fields[4],
                money_flag=list(fields[5:9]),
                ver=fields[9],
                undefine=fields[10],
                char_num=fields[11],
                sno=list(fields[12:24]),
                machine_sno=list(fields[24:48]),
                reserve1=fields[48],  # 调整索引
                image_sno=TImageSNo(
                    undefine=list(fields[49:53]),
                    sno=fields[53]
                )
            )

            # 解析结束标志（4字节0XBE）
            end_flag = data[-4:]
            if end_flag != b'\xBE\xBE\xBE\xBE':
                msg = f"recv end flag failed: end flag is not correct {end_flag}"
                logger.warning(msg)
                self.push_error(msg)
                return False
        except struct.error as e:
            msg = f"parse money data failed: {str(e)}"
            logger.error(msg)
            self.push_error(msg)
            return False

        return True


    # 推送数据
    def push_data(self) -> bool:
        # 只保留字母和数字，其余字符用空格代替
        sno_temp = ''.join(chr(c) for c in self.money_info.sno)
        sno_temp = re.sub(r'[^a-zA-Z0-9]', ' ', sno_temp)
        # 构造消息
        self.message = {
            "type": "serial_data",
            "data": {
                'date': f"{self.money_info.parsed_date}",
                'time': f"{self.money_info.parsed_time}",
                "tf_flag": f"{self.money_info.tf_flag}",
                'valuta': f"{self.money_info.valuta}",
                "fsn_count": f"{self.money_info.fsn_count}",
                'money_flag': self.money_info.currency_code,
                "ver": f"{self.money_info.ver}",
                "undefine": f"{self.money_info.undefine}",
                "char_num": f"{self.money_info.char_num}",
                "sno": sno_temp,
                "machine_number": ''.join(chr(c) for c in self.money_info.machine_number),
                "reserve1": f"{self.money_info.reserve1}",
                'image_data': self.image_opt.bmp_to_jpeg(add_bmp_headers(self.money_info.image_sno.sno)),
                'currency_name': self.money_info.parsed_currency,
                'create_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        # 将数据保存为图片
        # self.image_opt.save_base64_image(self.message['image_data'])

        # 存入队列
        try:
            message_queue.put(self.message)
        except Exception as e:
            msg = f"push data failed: {str(e)}"
            logger.error(msg)
            self.push_error(msg)
            return False
        return True


    # 数据入库
    def save_data(self) -> bool:
        try:
            # 数据入库（需要数据库实现）
            item_data = Result(
                date = self.message['data']['date'],
                time = self.message['data']['time'],
                tf_flag = self.message['data']["tf_flag"],
                valuta = self.message['data']['valuta'],
                fsn_count = self.message['data']["fsn_count"],
                money_flag = self.message['data']['money_flag'],
                ver = self.message['data']["ver"],
                undefine = self.message['data']["undefine"],
                char_num = self.message['data']["char_num"],
                sno = self.message['data']["sno"],
                machine_number = self.message['data']["machine_number"],
                reserve1 = self.message['data']["reserve1"],
                image_data = self.message['data']['image_data'],
                currency_name = self.message['data']['currency_name'],
            )
            self.db.add(item_data)
            self.db.commit()
            self.db.close()
        except Exception as e:
            error_msg = f"save data failed: {str(e)}"
            logger.error(error_msg)
            self.push_error(error_msg)
            return False
        return True

    # 推送错误提示信息
    def push_error(self, msg: str, type: str = "notification"):
        message = {
            "type": type,
            "data": msg
        }
        try:
            message_queue.put(message)
        except Exception as e:
            logger.error(f"push error failed: {str(e)}")
            return False
        return True