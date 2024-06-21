from pdf2image import convert_from_path
from flask import make_response
import os

def extract_image_from_pdf(path, page_number, left, top, right, bottom):
    '''
    pdf_path = " "
    page_number = 1
    left = 1898  # 左边界坐标
    top = 583  # 上边界坐标
    right = 2230  # 右边界坐标
    bottom = 1026  # 下边界坐标
    '''
    try:
        images = convert_from_path(path, dpi=300, first_page=page_number, last_page=page_number)
        image = images[0]

        cropped_image = image.crop((left, top, right, bottom))
        file_name = os.path.splitext(path)[0]  # 获取文件的基本名称（不包括扩展名）
        image_path = f"{file_name}_image.png"  # 拼接新的文件路径，包括正确的扩展名
        cropped_image.save(image_path)  # 将截取的图片保存到同一路径下
        return image_path
    except Exception as e:
        return make_response(f"<script>alert('从PDF提取图片错误: {e}'); window.location.href = document.referrer;</script>")




