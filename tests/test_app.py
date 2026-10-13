from io import BytesIO

import pytest
from conftest import synthetic_report
from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from app import create_app
from pdf_layout import text_origins


def test_conversion_retains_original_artwork_and_cleans_files(tmp_path, report_pdf):
    app = create_app({"TESTING": True, "TEMP_ROOT": str(tmp_path)})
    result = app.test_client().post("/convert", data={"file": (BytesIO(report_pdf), "报告.pdf")})
    assert result.status_code == 200
    assert result.mimetype == "application/pdf"
    before = PdfReader(BytesIO(report_pdf)).pages[0]
    after = PdfReader(BytesIO(result.data)).pages[0]
    assert before.mediabox == after.mediabox
    for name, image in before["/Resources"]["/XObject"].items():
        assert image.get_object()._data == after["/Resources"]["/XObject"][name].get_object()._data
    text = after.extract_text()
    assert "Beijing University of Technology" in text
    assert "Graduated" in text
    assert "Leaving date" in text
    assert "学校名称" not in text
    spans = text_origins(after)
    label = next(span for span in spans if span["text"] == "Verification code")
    code = next(span for span in spans if span["text"] == "EXAMPLE1234567890")
    assert label["size"] == 10
    assert label["y"] == code["y"]
    assert code["x"] >= label["x"] + stringWidth(label["text"], "Helvetica", 10) + 3
    assert list(tmp_path.iterdir()) == []


def test_unknown_translation_requires_real_english_name(monkeypatch, tmp_path, report_pdf):
    from converter import CHSIConverter, ConversionError

    source = tmp_path / "source.pdf"
    source.write_bytes(report_pdf)
    original = CHSIConverter.extract_info_from_pdf

    def unknown(path):
        info = original(path)
        info["Institution"] = "未收录测试大学"
        return info

    monkeypatch.setattr(CHSIConverter, "extract_info_from_pdf", unknown)
    with pytest.raises(ConversionError) as error:
        CHSIConverter.convert_to_pdf(source, tmp_path / "output.pdf")
    assert error.value.code == "missing_translation"
    CHSIConverter.convert_to_pdf(
        source, tmp_path / "output.pdf", {"Institution": "Test University"}
    )
    assert "Test University" in PdfReader(tmp_path / "output.pdf").pages[0].extract_text()
    with pytest.raises(ConversionError) as error:
        CHSIConverter.convert_to_pdf(
            source, tmp_path / "output.pdf", {"Institution": "Test University", "Name": "Ł Example"}
        )
    assert error.value.code == "invalid_translation"
    source.write_bytes(synthetic_report(branch="测试分院"))
    with pytest.raises(ConversionError) as error:
        CHSIConverter.convert_to_pdf(
            source, tmp_path / "output.pdf", {"Institution": "Test University"}
        )
    assert error.value.code == "unsupported_report"
