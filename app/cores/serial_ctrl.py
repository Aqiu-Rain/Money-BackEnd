# 导入系统库
from loguru import logger
import json
import struct
from dataclasses import asdict
import os
import sys
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
        ret = True
        if not self.serial_communication.is_connected():
            ret = self.serial_communication.open_connection()
            if ret:
                logger.info("connect successfully!")
        return ret
        
    # 关闭串口
    def close_connection(self):
        if self.serial_communication.is_connected():
            self.serial_communication.close_connection()
        
    # 数据接收及入库
    def recv_and_save_data(self):
        while True:
            if self.data_source == 'test':
                data = read_serial_data_from_file("tests/test_data/Log1.TXT")
            elif self.data_source == 'real':
                data = self.serial_communication.receive_data(1656)
            else:
                raise ValueError(f"Invalid data source: {self.data_source}")
            
            if not data:
                continue
            
            # 数据解析
            parsed = self.parse_data(bytes(data))
            if not parsed:
                continue
            
            # 测试
            # img_data= add_bmp_headers(parsed.image_sno.sno)
            # save_to_file(img_data)

            # 构造消息
            message = {
                "type": "serial_data",
                "data": {
                    'date': f"{parsed.parsed_date}",
                    'time': f"{parsed.parsed_time}",
                    "tf_flag": f"{parsed.tf_flag}",
                    'valuta': f"{parsed.valuta}",
                    "fsn_count": f"{parsed.fsn_count}",
                    'money_flag': parsed.currency_code,
                    "ver": f"{parsed.ver}",
                    "undefine": f"{parsed.undefine}",
                    "char_num": f"{parsed.char_num}",
                    "sno": ''.join(chr(c) for c in parsed.sno),
                    "machine_number": ''.join(chr(c) for c in parsed.machine_sno),
                    "reserve1": f"{parsed.reserve1}",
                    'image_data': self.image_opt.bmp_to_jpeg(add_bmp_headers(parsed.image_sno.sno)),
                    'currency_name': parsed.parsed_currency,
                }
            }
            
            # 将数据保存为图片
            # self.image_opt.save_base64_image(message['image_data'])
            
            # 存入队列
            message_queue.put(message)
            
            # 数据入库（需要数据库实现）
            item_data = Result(
                date = message['data']['date'],
                time = message['data']['time'],
                tf_flag = message['data']["tf_flag"],
                valuta = message['data']['valuta'],
                fsn_count = message['data']["fsn_count"],
                money_flag = message['data']['money_flag'],
                ver = message['data']["ver"],
                undefine = message['data']["undefine"],
                char_num = message['data']["char_num"],
                sno = message['data']["sno"],
                machine_number = message['data']["machine_number"],
                reserve1 = message['data']["reserve1"],
                image_data = message['data']['image_data'],
                currency_name = message['data']['currency_name'],
                calc_time = convert_to_datetime(message['data']['date'], message['data']['time'])
            )
            self.db.add(item_data)
            self.db.commit()
            self.db.close()

    # 解析数据
    def parse_data(self, data: bytes) -> BanknoteInfo:
        try:
            # 解析起始标志（4字节0XAE）
            start_flag = struct.unpack('4B', data[:4])
            if any(b != 0xAE for b in start_flag):
                return None
            
            # 解析消息长度（2字节）
            msg_length = struct.unpack('<H', data[4:6])[0]
            
            # 解析模式标志（2字节0X0001）
            mode_flag = struct.unpack('<H', data[6:8])[0]
            if mode_flag != 0x0001:
                return None
            
            # 解析纸币信息（1644字节）
            note_data = data[8:-4]
            if len(note_data) != 1644:
                return None
            
            # 解析结束标志（4字节0XBE）
            end_flag = struct.unpack('4B', data[-4:])
            if any(b != 0xBE for b in end_flag):
                return None
            
            # 修正后的格式字符串
            fmt = '<HHHIH4HHHH12H24HH4H1536s'  # 总长度=2+2+2+4+2+8+2+2+2+24+48+2+8+1536=1644
            
            fields = struct.unpack(fmt, note_data)
            
            return BanknoteInfo(
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
            
        except struct.error as e:
            logger.error(f"parse data failed: {str(e)}")
            return None
