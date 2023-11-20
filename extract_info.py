import re
from pypdf import PdfReader
from pypinyin import lazy_pinyin


def extract_text_from_pdf(pdf_path):
    pdf_file_obj = open(pdf_path, 'rb')
    pdf_reader = PdfReader(pdf_file_obj)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    pdf_file_obj.close()
    return text

def extract_info(patterns_dict, text):
    results = {}
    for prop, pattern in patterns_dict.items():
        match = re.search(pattern, text)
        if match:
            if prop == 'Name':
                pinyin = lazy_pinyin(match.group(1))
                first_char = pinyin[0].capitalize()
                remaining_chars = ''.join(pinyin[1:]).capitalize()
                results[prop] =  remaining_chars + ' ' + first_char
            elif prop == 'Gender':
                if match.group(1) == '男':
                    results[prop] = 'Male'
                elif match.group(1) == '女':
                    results[prop] = 'Female'
                else:
                    results[prop] = None
            elif prop == 'Ethnic':
                value = match.group(1)  
                pinyin_list = lazy_pinyin(value[:-1])  
                results[prop] = ''.join(pinyin_list).title()
            elif prop == 'Date of Birth' or prop == 'Date of Enrollment':
                value = match.group(1)  
                parts = value.split('年')
                year = parts[0]
                month_day = parts[1].split('月')
                formatted_date = month_day[0] + '/' + month_day[1].replace('日', '') + '/' + year
                results[prop] = formatted_date
            elif prop == 'Levels' :
                results[prop] = 'Undergraduate'
            elif prop == 'Form' :
                results[prop] = 'General full-time remote study'
            elif prop == 'Educational System':
                results[prop] = match.group(1)+' years'
            elif prop == 'Type':
                results[prop] = 'General higher education'
            elif prop == 'School Status':
                value = match.group(1)  
                date_part = value.split("：")[1]  
                parts = date_part.split('年')
                year = parts[0]
                month_day = parts[1].split('月')
                day = month_day[1].replace('日', '').replace('）', '')  # Remove trailing bracket from the day
                formatted_date = month_day[0] + '/' + day + '/' + year
                results[prop] = 'Student registration (Expected graduation date: ' + formatted_date + ')'
            elif prop == 'Update Date':
                value = match.group(1)  
                parts = value.split('年')
                year = parts[0]
                month_day = parts[1].split('月')
                formatted_date = month_day[0] + '/' + month_day[1].replace('日', '') + '/' + year
                results[prop] = formatted_date
            else:
                results[prop] = match.group(1)
        else:
            results[prop] = None
    return results

def extract_info_from_pdf(path):
    text = extract_text_from_pdf(path)

    def rc(pattern):
        return re.compile(r'{}\s*([^\s]*)'.format(pattern))

    patterns_dict = {
        'Update Date': rc('更新日期：'),
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

