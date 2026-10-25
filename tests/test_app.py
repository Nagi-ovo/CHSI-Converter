import logging
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


def test_missing_directories_are_created(tmp_path):
    from converter import CHSIConverter

    source = tmp_path / "source.pdf"
    source.write_bytes(synthetic_report())
    output = tmp_path / "missing" / "nested" / "output.pdf"
    CHSIConverter.convert_to_pdf(source, output)
    assert output.is_file()

    temp_root = tmp_path / "missing-temp-root" / "nested"
    create_app({"TESTING": True, "TEMP_ROOT": str(temp_root)})
    assert temp_root.is_dir()


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
    assert error.value.code == "missing_translation"
    assert "Branch" in error.value.diagnostic
    CHSIConverter.convert_to_pdf(
        source,
        tmp_path / "output.pdf",
        {"Institution": "Test University", "Branch": "Test Branch"},
    )
    assert "Test Branch" in PdfReader(tmp_path / "output.pdf").pages[0].extract_text()


def test_branch_override_is_accepted_by_web_form(tmp_path):
    report = synthetic_report(branch="测试分院")
    app = create_app({"TESTING": True, "TEMP_ROOT": str(tmp_path)})
    result = app.test_client().post(
        "/convert",
        data={
            "file": (BytesIO(report), "report.pdf"),
            "branch": "Test Branch",
        },
    )
    assert result.status_code == 200
    assert "Test Branch" in PdfReader(BytesIO(result.data)).pages[0].extract_text()
    assert list(tmp_path.iterdir()) == []


def test_missing_translation_page_shows_field_status(tmp_path):
    report = synthetic_report(branch="测试分院")
    app = create_app({"TESTING": True, "TEMP_ROOT": str(tmp_path)})
    result = app.test_client().post("/convert", data={"file": (BytesIO(report), "report.pdf")})
    assert result.status_code == 422
    html = result.get_data(as_text=True)
    assert "译名识别结果" in html
    assert "学校" in html
    assert "Beijing University of Technology" in html
    assert "专业" in html
    assert "Artificial Intelligence" in html
    assert "分院" in html
    assert "测试分院" in html
    assert "需要补充英文名" in html
    assert list(tmp_path.iterdir()) == []


def test_unsupported_report_logs_only_safe_metadata(caplog, tmp_path):
    report = synthetic_report(include_title=False)
    app = create_app({"TESTING": True, "DEBUG": True, "TEMP_ROOT": str(tmp_path)})
    with caplog.at_level(logging.INFO):
        result = app.test_client().post("/convert", data={"file": (BytesIO(report), "report.pdf")})
    assert result.status_code == 422
    assert "outcome=unsupported_report" in caplog.text
    assert "diagnostic=" not in caplog.text
    assert "traceback" not in caplog.text
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("debug", [False, True])
def test_worker_exception_does_not_log_personal_fields(caplog, tmp_path, debug):
    from pypdf import PdfWriter
    from reportlab.pdfgen.canvas import Canvas

    marker = "1996/02/03_PRIVATE_SENTINEL"
    report = synthetic_report()
    overlay = BytesIO()
    page = Canvas(overlay)
    page.setFont("STSong-Light", 10)
    page.drawString(60, 440, "出生日期")
    page.drawString(179, 440, marker)
    page.save()
    writer = PdfWriter(clone_from=BytesIO(report))
    writer.pages[0].merge_page(PdfReader(BytesIO(overlay.getvalue())).pages[0])
    document = BytesIO()
    writer.write(document)
    document.seek(0)
    app = create_app({"TESTING": True, "DEBUG": debug, "TEMP_ROOT": str(tmp_path)})
    with caplog.at_level(logging.INFO):
        result = app.test_client().post("/convert", data={"file": (document, "report.pdf")})
    assert result.status_code == 500
    assert "outcome=failed" in caplog.text
    assert marker not in caplog.text
    assert marker not in result.get_data(as_text=True)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("debug", [False, True])
def test_application_exception_does_not_log_report_values(caplog, tmp_path, report_pdf, debug):
    marker = "PRIVATE_APPLICATION_SENTINEL"

    def failing_converter(*_args):
        raise ValueError(marker)

    app = create_app(
        {
            "TESTING": True,
            "DEBUG": debug,
            "TEMP_ROOT": str(tmp_path),
            "CONVERTER": failing_converter,
        }
    )
    with caplog.at_level(logging.INFO):
        result = app.test_client().post(
            "/convert", data={"file": (BytesIO(report_pdf), "report.pdf")}
        )
    assert result.status_code == 500
    assert "outcome=failed" in caplog.text
    assert marker not in caplog.text
    assert marker not in result.get_data(as_text=True)
    assert list(tmp_path.iterdir()) == []
