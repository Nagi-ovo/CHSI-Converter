import re
import PyPDF2

def extract_text_from_pdf(pdf_path):
    pdf_file_obj = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    pdf_file_obj.close()
    return text

def extract_info(patterns_dict, text):
    results = {}
    for prop, pattern in patterns_dict.items():
        match = re.search(pattern, text)
        results[prop] = match.group(1) if match else None
    return results

def extract_info_from_pdf(path):
    text = extract_text_from_pdf(path)

    def rc(pattern):
        return re.compile(r'{}\s*([^\s]*)'.format(pattern))

    patterns_dict = {
        'Name': rc('姓名'),
        'Gender': rc('性别'),
        'Id Number': rc('证件号码'),
        'Ethnic': rc('民族'),
        'Date of Birth': rc('出生日期 '),
        'Institution': rc('院校'),
        'Levels': rc('层次'),
        'Faculties': rc('院系'),
        'Class': rc('班级'),
        'Major': rc('专业'),
        'Student Number': rc('学号'),
        'Form': rc('形式'),
        'Date of Enrollment': rc('入学日期'),
        'Educational System': rc('学制'),
        'Type': rc('类型'),
        'School Status': rc('学籍状态'),
    }
    
    # 获取匹配的信息
    results = extract_info(patterns_dict, text)
    
    return results
