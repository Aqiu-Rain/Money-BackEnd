# 系统标准库
import os
import io
import base64
import struct
from loguru import logger
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

# 第三方库
# 这里没有第三方库导入
from PIL import Image

# 自定义库
# 这里没有自定义库导入

@dataclass
class ImageSaveConfig:
    """图像保存配置"""
    base_dir: str = "images"                # 基础保存目录
    use_date_subdir: bool = True           # 是否使用日期子目录
    filename_template: str = "{date}_{time}_{currency}_{sno}"  # 文件名模板
    overwrite: bool = False                # 是否覆盖已存在文件
    max_files_per_dir: int = 1000          # 每个目录最大文件数
    save_as_base64: bool = True           # 是否保存为base64文本文件

class ImageSaverService:
    """图像保存服务"""
    
    def __init__(self, config: Optional[ImageSaveConfig] = None):
        """
        初始化图像保存服务
        :param config: 保存配置，如果为None则使用默认配置
        """
        self.config = config or ImageSaveConfig()
        
        # 确保基础目录存在
        os.makedirs(self.config.base_dir, exist_ok=True)
    
    def save_image(self, image_data: bytes, metadata: Dict[str, Any]) -> str:
        """
        保存图像数据到文件
        :param image_data: 图像数据，可以是bytes或16进制字符串
        :param metadata: 图像元数据，用于生成文件名
        :return: 保存的文件路径
        """
        logger.debug("entry save_iamge")
        try:
            # 1. 将16进制数据转换为base64
            base64_data = self.convert_to_base64(image_data)

            # 2. 确定保存目录
            save_dir = self._get_save_directory(metadata)
            
            # 3. 生成文件名
            filename = self._generate_filename(metadata)
            
            # 4. 构建完整路径
            if self.config.save_as_base64:
                # 保存为base64文本文件
                filepath = Path(save_dir) / f"{filename}.txt"
                with open(filepath, 'w') as f:
                    f.write(base64_data.decode('ascii'))
            else:
                # 保存为二进制图片文件
                filepath = Path(save_dir) / f"{filename}.bmp"
                # 将base64解码回二进制
                binary_data = base64.b64decode(base64_data)
                
                # 检查文件是否已存在
                if filepath.exists() and not self.config.overwrite:
                    # 添加序号避免覆盖
                    counter = 1
                    while filepath.exists():
                        filepath = Path(save_dir) / f"{filename}_{counter}.bmp"
                        counter += 1
                
                # 写入文件
                with open(filepath, 'wb') as f:
                    f.write(binary_data)
            
            self.logger.info(f"图像已保存: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"图像保存失败: {str(e)}")
            raise
    
    def save_base64_image(self, image_data: str):
        # 判断是否为base64数据格式
        # 保存到文件
        with open(self.filepath, 'wb') as f:
            f.write(image_data)

    def convert_to_base64(self, data: Union[bytes, str]) -> str:
        """
        将16进制数据转换为base64编码
        :param data: 16进制数据，可以是bytes或字符串
        :return: base64编码的bytes对象
        """
        # 如果是字符串，先转换为bytes
        if isinstance(data, str):
            # 假设是16进制字符串
            data = bytes.fromhex(data)
        
        # 转换为base64
        return base64.b64encode(data).decode()


    def _get_save_directory(self, metadata: Dict[str, Any]) -> str:
        """确定保存目录"""
        if not self.config.use_date_subdir:
            return self.config.base_dir
            
        # 使用日期作为子目录
        today = datetime.now().strftime("%Y%m%d")
        save_dir = os.path.join(self.config.base_dir, today)
        os.makedirs(save_dir, exist_ok=True)
        
        return save_dir
    
    def _generate_filename(self, metadata: Dict[str, Any]) -> str:
        """根据元数据生成文件名"""
        # 提取常用字段，处理可能缺失的情况
        date_str = metadata.get('date', datetime.now().strftime("%Y%m%d"))
        time_str = metadata.get('time', datetime.now().strftime("%H%M%S"))
        currency = metadata.get('currency_code', 'UNKNOWN')
        sno = metadata.get('sno', '')[:4]  # 取冠字号码前4位
        
        # 使用模板格式化文件名
        filename = self.config.filename_template.format(
            date=date_str,
            time=time_str,
            currency=currency,
            sno=sno,
            **metadata  # 允许使用其他元数据字段
        )
        
        # 移除文件名中的非法字符
        filename = self._sanitize_filename(filename)
        return filename
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """移除文件名中的非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def bmp_to_jpeg(self, bmp_data: bytes) -> str:
        pil_image = Image.open(io.BytesIO(bmp_data))

        # 将图片转换为PNG格式
        png_io = io.BytesIO()
        pil_image.save(png_io, format='PNG')
        png_data = png_io.getvalue()

        # 将PNG数据准换为base64编码字符串
        return base64.b64encode(png_data).decode('utf-8')
    


def add_bmp_headers(pixel_data: bytes) -> bytes:
    """
    为灰度图像数据添加BMP文件头和信息头
    参数：
        pixel_data: 原始像素数据 (96x16 8-bit灰度)
    返回：
        完整的BMP文件字节数据
    """
    # 基本参数
    width = 96
    height = 16
    bpp = 8  # 8位灰度
    image_size = len(pixel_data)  # 96*16=1536
    
    # 1. 创建调色板（256色灰度）
    palette = bytearray()
    for i in range(256):
        palette.extend((i, i, i, 0))  # BGR + reserved
    
    # 2. 计算各段大小
    file_header_size = 14
    info_header_size = 40
    palette_size = len(palette)  # 256*4=1024
    pixel_offset = file_header_size + info_header_size + palette_size  # 14+40+1024=1078
    
    # 3. 构建文件头 (BITMAPFILEHEADER)
    file_header = struct.pack(
        '<2sIHHI',
        b'BM',                  # 文件类型
        file_header_size + info_header_size + palette_size + image_size,  # 总文件大小
        0,                      # 保留
        pixel_offset,           # 像素数据偏移量
        file_header_size + info_header_size # 头信息总大小
    )

    # 4. 构建信息头 (BITMAPINFOHEADER)
    info_header = struct.pack(
        '<IIiHHIIIIII',
        info_header_size,       # 信息头大小
        width,                  # 宽度
        -height,                # 高度(负数表示从上到下存储)
        1,                      # 颜色平面数
        bpp,                    # 每像素位数
        0,                      # 压缩方式(BI_RGB)
        image_size,             # 图像数据大小
        2835,                   # 水平分辨率(72 DPI)
        2835,                   # 垂直分辨率
        256,                    # 使用的颜色数
        256                     # 重要颜色数
    )

    # 5. 组合所有部分
    return file_header + info_header + palette + pixel_data

