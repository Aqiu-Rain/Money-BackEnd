import os
import uuid
import shutil
from datetime import datetime

import base64
import binascii


def split_list(input_list, n):
    # 使用列表推导式和切片
    return [input_list[i:i + n] for i in range(0, len(input_list), n)]


def rename_file(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + '-' + str(int(datetime.utcnow().timestamp())) + ext
    return new_filename


def delete_file(filename):
    try:
        os.remove(filename)
        return True, '文件已删除'
    except FileNotFoundError:
        return False, '文件不存在'


def remove_folder(folder):
    shutil.rmtree(folder)
    return True, '文件夹已删除'


def convert_to_datetime(date_str, time_str):
    """
    将日期字符串和时间元组字符串转换为datetime对象。
    
    参数:
        date_str (str): 日期字符串，格式为 'YYYY-MM-DD'。
        time_str (str): 时间元组字符串，格式为 '(HH, MM, SS)'。
    
    返回:
        datetime: datetime对象。
    """
    # 解析日期字符串
    year, month, day = map(int, date_str.split('-'))
    
    # 解析时间元组字符串
    time_tuple = eval(time_str)  # 将字符串转换为元组
    hour, minute, second = time_tuple
    
    # 创建datetime对象
    dt = datetime(year, month, day, hour, minute, second)
    
    return dt