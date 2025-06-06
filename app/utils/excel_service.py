import os
from datetime import datetime
import base64
import getpass
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from io import BytesIO
from PIL import Image as PILImage  # 需要安装pillow包

def export_to_excel(data, file_name):
    # 初始化工作簿
    wb = Workbook()
    ws = wb.active
    
    # 添加表头
    headers = list(data[0].keys()) if data else []
    ws.append(headers)
    
    # 预设参数
    DEFAULT_ROW_HEIGHT = 20  # 默认行高（单位：磅）
    MAX_IMAGE_WIDTH = 200    # 图片最大宽度（像素）
    PIXELS_PER_POINT = 1.33  # 1磅≈1.33像素
    
    # 添加数据行
    for idx, row in enumerate(data, start=2):
        # 设置默认行高
        ws.row_dimensions[idx].height = DEFAULT_ROW_HEIGHT
        
        # 处理图片
        if 'S.N. Image' in row and row['S.N. Image']:
            try:
                # 解码图片并获取原始尺寸
                img_data = base64.b64decode(row['S.N. Image'])
                pil_img = PILImage.open(BytesIO(img_data))
                original_width, original_height = pil_img.size
                
                # 计算最大允许高度（单位：像素）
                max_height_pixels = DEFAULT_ROW_HEIGHT * PIXELS_PER_POINT
                
                # 计算缩放比例（同时考虑宽度和高度限制）
                width_scale = MAX_IMAGE_WIDTH / original_width
                height_scale = max_height_pixels / original_height
                scale_factor = min(width_scale, height_scale)
                
                # 计算目标尺寸
                target_width = int(original_width * scale_factor)
                target_height = int(original_height * scale_factor)
                
                # 创建Excel图片对象
                img = Image(BytesIO(img_data))
                img.width = target_width
                img.height = target_height
                
                # 插入图片并更新标注
                ws.add_image(img, f'H{idx}')
                row['S.N. Image'] = f'见H{idx}单元格图片'
                
                # 调整列宽适应图片
                col_letter = 'H'
                required_col_width = max(
                    ws.column_dimensions[col_letter].width or 0,
                    target_width / 7  # 1字符≈7像素
                )
                ws.column_dimensions[col_letter].width = required_col_width
                
            except Exception as e:
                print(f"处理第{idx}行图片时出错: {e}")
                row['S.N. Image'] = '图片加载失败'
        
        # 添加数据
        ws.append(list(row.values()))
    
    # 自动调整所有列宽（排除图片列）
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        if col_letter == 'H':  # 跳过图片列
            continue
            
        for cell in col:
            try:
                max_length = max(max_length, len(str(cell.value or "")))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[col_letter].width = adjusted_width
    
    # 保存文件
    user = getpass.getuser()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop_path = os.path.join(f"C:/Users/{user}/Desktop", 'GraceTek')
    os.makedirs(desktop_path, exist_ok=True)
    
    file_path = os.path.join(desktop_path, f'report_{timestamp}.xlsx')
    wb.save(file_path)
    
    return file_path