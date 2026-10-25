from io import BytesIO

import pytest
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen.canvas import Canvas


def synthetic_report(branch=None, include_title=True):
    """Artificial data with original artwork and separate label/value positions."""
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    stream = BytesIO()
    page = Canvas(stream, pagesize=A4)
    page.setStrokeColorRGB(0.2, 0.6, 0.5)
    page.rect(25, 25, 545, 792)
    page.drawImage(ImageReader(Image.new("RGB", (10, 10), "blue")), 455, 600, 80, 100)
    if include_title:
        page.setFont("STSong-Light", 20)
        page.drawString(180, 768, "教育部学籍在线验证报告")
    page.setFont("STSong-Light", 10)
    page.drawString(220, 746, "更新日期：2024年1月15日")
    for index, (label, value) in enumerate(
        [
            ("姓名", "测试样本"),
            ("学校名称", "北京工业大学"),
            ("专业", "人工智能"),
            ("系所", "信息科学技术学院"),
            ("学籍状态", "不在籍（毕业）"),
            ("离校日期", "2023年6月30日"),
        ]
    ):
        page.drawString(60, 708 - index * 28, label)
        page.drawString(179, 708 - index * 28, value)
    if branch:
        page.drawString(60, 500, "分院")
        page.drawString(179, 500, branch)
    page.setFont("STSong-Light", 10)
    page.drawString(163.79, 169.33, "在线验证码")
    page.setFont("STSong-Light", 15)
    page.setFillColorRGB(0, 0.7, 0.74)
    page.drawString(216.03, 169.33, "EXAMPLE1234567890")
    page.save()
    return stream.getvalue()


@pytest.fixture
def report_pdf():
    return synthetic_report()
