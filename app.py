from docx.oxml import OxmlElement
from flask import Flask, request, send_file, render_template, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
from add_float_picture import add_float_picture
from extract_img import extract_image_from_pdf
from extract_info import extract_info_from_pdf
import sys
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import uuid

app = Flask(__name__)

# 你的转换函数

def convert_to_docx(path):
    extracted_info = extract_info_from_pdf(path)
    doc = Document("static/template.docx")

    paragraph = doc.add_paragraph()
    doc.element.body.insert(1, paragraph._element)
    paragraph.alignment = 1
    paragraph.add_run('Update date:' + extracted_info['Update Date'])

    del extracted_info['Update Date']

    table = doc.add_table(rows=1, cols=2)
    table.autofit = False


    for cell in table.columns[0].cells:
        cell.width = Inches(0.5)
    for cell in table.columns[1].cells:
        cell.width = Inches(5.0)

    border_xml = '<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' \
                '<w:top w:val="nil"/>' \
                '<w:left w:val="nil"/>' \
                '<w:bottom w:val="nil"/>' \
                '<w:right w:val="nil"/>' \
                '</w:tcBorders>'

    for key, value in extracted_info.items():
        cells = table.add_row().cells
        for cell in cells:
            cell._element.get_or_add_tcPr().append(parse_xml(border_xml))
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        cells[0].text = key
        cells[1].text = value + "\n"

    cropped_image_1 = extract_image_from_pdf(path, 1, 1898, 583, 2230, 1026)
    add_float_picture(doc.add_paragraph(), cropped_image_1, width=Inches(1.2), pos_x=Pt(430), pos_y=Pt(140))

    cropped_image_2 = extract_image_from_pdf(path, 1, 300, 2690, 630, 2985)
    add_float_picture(doc.add_paragraph(), cropped_image_2, width=Inches(1.2), pos_x=Pt(78), pos_y=Pt(643))

    output_path = path.replace(".pdf", ".docx")
    doc.save(output_path)

    return output_path

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('upload', filename)
        file.save(filepath)

        output_path = convert_to_docx(filepath)

        directory = os.path.dirname(output_path)
        filename = os.path.basename(output_path)
        output_filename = str(uuid.uuid4()) + '.docx'

        response = make_response(send_from_directory(directory, filename, as_attachment=True))
        response.headers["Content-Disposition"] = f"attachment; filename={output_filename}"
        return response

if __name__ == '__main__':
    app.run(debug=True)
