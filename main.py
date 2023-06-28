from tkinter import Tk, Button, Label, StringVar
from tkinter.filedialog import askopenfilename
from docx import Document
from docx.shared import Inches,Pt
import os
import subprocess
import sys
from extract_info import extract_info_from_pdf
from extract_img import extract_image_from_pdf
from add_float_picture import add_float_picture


def open_docx_on_desktop(file_path):
    # 根据操作系统选择适当的命令
    if sys.platform.startswith('darwin'):  # macOS
        command = ['open', file_path]
    elif sys.platform.startswith('win32'):  # Windows
        os.startfile(file_path)
    elif sys.platform.startswith('linux'):  # Linux
        command = ['xdg-open', file_path]
    else:
        print("无法识别的操作系统")
        return

    # 执行命令
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print("无法打开文件:", e)


# 创建根窗口
root = Tk()
root.title("EZ4STU")
root.geometry("600x400")
root.configure(bg='lightblue')

# 创建顶部标题标签
title_label = Label(root, text="PDF to DOCX Converter", font=("Helvetica", 24, "bold"), bg='lightblue', fg='white')
title_label.pack(pady=20)

# 创建文件路径变量
file_path = StringVar()
file_path.set("请选择要转换的PDF文件")

# 创建转换后文件路径变量
converted_file_path = StringVar()
converted_file_path.set("")

# 选择文件按钮点击事件处理函数
def select_file():
    # 弹出文件选择对话框并更新文件路径变量
    path = askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    file_path.set(path)

# 创建选择文件按钮
select_button = Button(root, text="选择文件", command=select_file, font=("Arial", 16), bg='white', fg='black')
select_button.pack(pady=10)

# 创建文件路径标签
file_label = Label(root, textvariable=file_path, font=("Arial", 14), bg='lightblue', fg='white')
file_label.pack(pady=10)

# 转换函数
def convert_to_docx():
    path = file_path.get()
    if path:
        # 提取PDF中的文本内容
        extracted_info = extract_info_from_pdf(path)

        # 提取PDF中的图片
        cropped_image = extract_image_from_pdf(path, 1, 1898, 583, 2230, 1026)

        # 用提取的信息和图片创建一个新的docx文档
        doc = Document("template.docx")
        
        for key, value in extracted_info.items():
            paragraph = doc.add_paragraph()
            space_replace = key.replace(' ', '')
            num_spaces = int(45 - (len(space_replace) * 2 + (len(key) - len(space_replace)) * 1))
            run = paragraph.add_run(f"{key}{' ' * num_spaces}{value}\n")

            print(len(space_replace) * 2 + (len(key) - len(space_replace)) * 1)

            run.font.size = Pt(11)  # 设置字体大小
            run.font.bold = True  # 设置字体为加粗

        add_float_picture(doc.add_paragraph(), cropped_image, width=Inches(1.2), pos_x=Pt(430), pos_y=Pt(140))

        # 保存为docx文件
        output_path = path.replace(".pdf", ".docx")
        doc.save(output_path)

        # 显示文件路径
        converted_file_path.set("已转换为DOCX文件：\n" + output_path)

        # 打开生成的文件
        root.after(1500, lambda: open_docx_on_desktop(output_path))
        
    else:
        file_path.set("请先选择一个PDF文件")

# 创建转换按钮
convert_button = Button(root, text="转换", command=convert_to_docx, font=("Arial", 16), bg='white', fg='black')
convert_button.pack(pady=20)

# 创建转换后文件路径标签
converted_file_label = Label(root, textvariable=converted_file_path, font=("Arial", 14), bg='lightblue', fg='white')
converted_file_label.pack(pady=10)

root.mainloop()
