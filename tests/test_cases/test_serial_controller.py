# 导入系统库
import logging
import unittest
import time
import json
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入第三方库

# 导入自定义库
from src.controller.serial_controller import SerialController, message_queue

class TestSerialController(unittest.TestCase):
    def setUp(self):
        self.controller = SerialController()
        
        # 构造符合SerialParameters要求的JSON参数
        self.test_params = {
            "port": "COM1",
            "baudrate": 115200,
            "bytesize": 8,
            "parity": 'N',
            "stopbits": 1,
            "timeout": 1.0,
            "xonxoff": False,
            "rtscts": False,
            "dsrdtr": False
        }

    def test_serial_workflow(self):
        # 设置串口参数
        self.controller.set_serial_param(self.test_params)

        # 打开串口
        ret = self.controller.open_connection()
        self.assertTrue(ret)
        
        # 启动数据接收线程
        recv_thread = threading.Thread(target=self.controller.recv_and_save_data, daemon=True)
        recv_thread.start()
        
        # 添加测试超时机制
        start_time = time.time()
        while True:  # 5秒超时
            time.sleep(1)
            # if not message_queue.empty():
            #     msg = message_queue.get()
            #     print("\n解析到的纸币信息：")
            #     print(f"日期: {msg['date']}")
            #     print(f"时间: {msg['time']}")
            #     print(f"币值: {msg['currency_value']}")
            #     print(f"冠字号码: {msg['serial_number']}")
            #     print(f"机具编号: {msg['machine_number']}")
            #     print(f"真伪: {'真币' if msg['is_genuine'] else '假币'}")
            
                # 显示BMP图像数据（前100字节示例）
                # print("\nBMP图像数据（部分）：")
                # print(msg['image_data'][:200] + "...")
            
                # 实际显示图像需要完整数据
                # try:
                #     img_bytes = bytes.fromhex(msg['image_data'])
                #     img = Image.open(io.BytesIO(img_bytes))
                #     img.show()  # 会自动调用系统图片查看器
                #     print("成功显示BMP图像")
                # except Exception as e:
                #     print(f"图像显示失败: {str(e)}")
                # return  # 成功获取数据后退出测试
            
        self.fail("测试超时，未收到任何数据")

if __name__ == '__main__':
    unittest.main(exit=False)  # 修改这里避免直接调用sys.exit() 
