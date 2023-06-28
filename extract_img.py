from pdf2image import convert_from_path
from PIL import Image

def extract_image_from_pdf(path, page_number, left, top, right, bottom):
    images = convert_from_path(path, dpi=300, first_page=page_number, last_page=page_number)
    image = images[0]

    cropped_image = image.crop((left, top, right, bottom))
    image_path = path.replace(".pdf", "_image.png")
    cropped_image.save(image_path)  # 将截取的图片保存到同一路径下
    return image_path

pdf_path = "教育部学籍在线验证报告_张泽西.pdf"
page_number = 1
left = 1898  # 左边界坐标
top = 583  # 上边界坐标
right = 2230  # 右边界坐标
bottom = 1026  # 下边界坐标



