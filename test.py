from tkinter import Tk, Button, Label, StringVar
from tkinter.filedialog import askopenfilename
from docx import Document
import PyPDF2
import os
import subprocess
import sys

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
        pdf_file = open(path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # 创建一个新的docx文档并将文本添加到段落中
        doc = Document()
        doc.add_paragraph(text)

        # 保存为docx文件
        output_path = path.replace(".pdf", ".docx")
        doc.save(output_path)

        # 显示文件路径
        converted_file_path.set("已转换为DOCX文件：\n" + output_path)
        print(output_path)
        # 打开生成的文件
        root.after(3000, lambda: open_docx_on_desktop(output_path))
        
    else:
        file_path.set("请先选择要转换的PDF文件")

# 创建转换按钮
convert_button = Button(root, text="转换为DOCX", command=convert_to_docx, font=("Arial", 16), bg='white', fg='black')
convert_button.pack(pady=10)

# 创建转换后的文件路径标签
converted_file_label = Label(root, textvariable=converted_file_path, font=("Arial", 14), bg='lightblue', fg='white')
converted_file_label.pack(pady=10)

# 运行主循环
root.mainloop()
