from io import BytesIO

import pytest
from conftest import synthetic_report
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import (
    ArrayObject,
    ByteStringObject,
    ContentStream,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    TextStringObject,
)
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from converter import CHSIConverter
from pdf_layout import text_origins


def page_with_text(operations):
    stream = BytesIO()
    drawing = Canvas(stream)
    drawing.drawString(1, 1, "font resources")
    drawing.save()
    page = PdfReader(stream).pages[0]
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 10 Tf 1 0 0 1 50 700 Tm " + operations + b" ET")
    page[NameObject("/Contents")] = content
    return page


def test_continuous_operations_and_whitespace_keep_origins():
    spans = text_origins(page_with_text(b"(A) Tj ( ) Tj (B) Tj 0 -20 Td (C) Tj"))
    assert [span["text"] for span in spans] == ["A", "B", "C"]
    assert spans[1]["x"] == pytest.approx(50 + stringWidth("A ", "Helvetica", 10))
    assert (spans[2]["x"], spans[2]["y"]) == pytest.approx((50, 680))


def test_tj_numeric_adjustments_preserve_spacing_and_following_origin():
    spans = text_origins(page_with_text(b"[(A) 100 (B) -300 (C)] TJ (D) Tj"))
    # A/B touch (negative kerning); the explicit C gap remains separate.
    assert [span["text"] for span in spans] == ["AB", "CD"]
    expected = 50 + stringWidth("AB", "Helvetica", 10) + 2
    assert spans[1]["x"] == pytest.approx(expected)


@pytest.mark.parametrize("quote", [b"(B) '", b'3 2 (B) "'])
def test_quote_operators_move_to_next_text_line(quote):
    spans = text_origins(page_with_text(b"12 TL (A) Tj " + quote + b" (C) Tj"))
    assert [span["text"] for span in spans] == ["A", "BC"]
    assert (spans[1]["x"], spans[1]["y"]) == pytest.approx((50, 688))


@pytest.mark.parametrize(
    "mode", ["array", "split_operations", "split_blocks", "quote", "double_quote"]
)
def test_equivalent_report_text_operations_convert_and_preserve_artwork(tmp_path, mode):
    writer = PdfWriter(clone_from=BytesIO(synthetic_report()))
    page = writer.pages[0]
    writer.add_annotation(
        0, Link(rect=(216.03, 165, 350, 186), url="https://www.chsi.com.cn/verify")
    )
    writer.add_annotation(0, Link(rect=(50, 50, 100, 80), url="https://untrusted.example/"))
    writer.root_object[NameObject("/OpenAction")] = DictionaryObject(
        {NameObject("/S"): NameObject("/JavaScript"), NameObject("/JS"): TextStringObject("test")}
    )
    content = ContentStream(page.get_contents(), writer)
    operations = []
    font_size = 10
    matrix = None
    for args, op in content.operations:
        if op == b"Tf":
            font_size = float(args[1])
        elif op == b"Tm":
            matrix = args
        if op != b"Tj":
            operations.append((args, op))
            continue
        raw = args[0].original_bytes
        if mode == "array":
            operations.append(([ArrayObject([ByteStringObject(raw)])], b"TJ"))
        elif mode == "split_operations":
            for start in range(0, len(raw), 2):
                operations.append(([ByteStringObject(raw[start : start + 2])], b"Tj"))
        elif mode in {"quote", "double_quote"}:
            # Zero leading preserves the original position while testing the
            # alternate text operators in an entire convertible report.
            operations.append(([FloatObject(0)], b"TL"))
            if mode == "quote":
                operations.append(([ByteStringObject(raw)], b"'"))
            else:
                operations.append(([FloatObject(0), FloatObject(0), ByteStringObject(raw)], b'"'))
        else:
            # The two pieces touch visually but have separate text objects.
            middle = len(raw) // 4 * 2
            first = raw[:middle]
            offset = stringWidth(first.decode("utf-16-be"), "STSong-Light", font_size)
            operations.extend(
                [
                    ([ByteStringObject(first)], b"Tj"),
                    ([], b"ET"),
                    ([], b"BT"),
                    ([*matrix[:4], FloatObject(float(matrix[4]) + offset), matrix[5]], b"Tm"),
                    ([ByteStringObject(raw[middle:])], b"Tj"),
                ]
            )
    content.operations = operations
    page.replace_contents(content)
    source, output = tmp_path / "source.pdf", tmp_path / "output.pdf"
    writer.write(source)
    CHSIConverter.convert_to_pdf(source, output)
    result = PdfReader(output)
    after = result.pages[0]
    assert "/OpenAction" not in result.trailer["/Root"]
    assert len(after["/Annots"]) == 1
    annotation = after["/Annots"][0].get_object()
    assert annotation["/A"]["/URI"] == "https://www.chsi.com.cn/verify"
    assert float(annotation["/Rect"][0]) > 216.03
    text = after.extract_text()
    assert "Online Verification Report of Student Record" in text
    assert "Beijing University of Technology" in text
    assert "Graduated" in text
    assert "学校名称" not in text
    for name, image in page["/Resources"]["/XObject"].items():
        assert image.get_object()._data == after["/Resources"]["/XObject"][name].get_object()._data


def test_leading_trailing_and_blank_runs_keep_visible_positions():
    spans = text_origins(page_with_text(b"(  A ) Tj (B) Tj ( ) Tj ( C) Tj"))
    assert [span["text"] for span in spans] == ["A", "B", "C"]
    for span, prefix in zip(spans, ["  ", "  A ", "  A B  "]):
        assert span["x"] == pytest.approx(50 + stringWidth(prefix, "Helvetica", 10))


def test_spacing_and_graphics_restore_affect_following_origins():
    spans = text_origins(page_with_text(b"2 Tc 3 Tw 50 Tz (A ) Tj q 0 Tc 0 Tw (B) Tj Q (C) Tj"))
    assert [span["text"] for span in spans] == ["A", "BC"]
    expected = 50 + (stringWidth("A ", "Helvetica", 10) + 7) * 0.5
    assert spans[1]["x"] == pytest.approx(expected)


def test_distant_columns_do_not_merge():
    spans = text_origins(page_with_text(b"(Label) Tj 119 0 Td (Value) Tj"))
    assert [span["text"] for span in spans] == ["Label", "Value"]
    assert spans[1]["x"] == 169


def test_text_run_limit_stays_in_force():
    with pytest.raises(ValueError, match="Too many text runs"):
        text_origins(page_with_text(b"[(A)] TJ " * 1001))
