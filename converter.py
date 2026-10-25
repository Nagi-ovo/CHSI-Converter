"""Translate CHSI text in place while retaining the original PDF artwork."""

import json
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, ContentStream, NameObject, RectangleObject
from pypinyin import lazy_pinyin
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from pdf_layout import adjacent_text_x, text_origins
from translations import FOOTNOTES, LABELS

VERIFICATION_LABEL = "Verification code"

UNIVERSITY_NAMES = json.loads(
    (Path(__file__).parent / "data" / "university_names.json").read_text(encoding="utf-8")
)


class ConversionError(Exception):
    def __init__(self, code, diagnostic=None, details=None):
        super().__init__(diagnostic or code)
        self.code = code
        self.diagnostic = diagnostic or code
        self.details = details or {}


class CHSIConverter:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        try:
            reader = PdfReader(pdf_path)
            if reader.is_encrypted:
                raise ConversionError("encrypted_pdf", "PDF is encrypted")
            if not 1 <= len(reader.pages) <= 10:
                raise ConversionError(
                    "too_complex", f"expected 1-10 pages, found {len(reader.pages)}"
                )
            first = reader.pages[0]
            scale = float(first.user_unit) * 300 / 72
            width, height = (
                float(first.mediabox.width) * scale,
                float(first.mediabox.height) * scale,
            )
            if width <= 0 or height <= 0 or width * height > 12_000_000:
                raise ConversionError(
                    "too_complex",
                    f"page area exceeds limit: width={width:.1f}, height={height:.1f}",
                )
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if len(text) > 1_000_000:
                raise ConversionError(
                    "too_complex", f"extracted text exceeds limit: chars={len(text)}"
                )
            return text
        except ConversionError:
            raise
        except Exception as error:
            raise ConversionError(
                "invalid_pdf", f"PDF parser failed: {type(error).__name__}: {error}"
            ) from None

    @staticmethod
    def extract_info(patterns_dict, text):
        results = {}
        for prop, pattern in patterns_dict.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                if prop == "Name":
                    pinyin = lazy_pinyin(value)
                    results[prop] = f"{''.join(pinyin[1:]).capitalize()} {pinyin[0].capitalize()}"
                elif prop == "Gender":
                    results[prop] = "Male" if value == "男" else "Female" if value == "女" else None
                elif prop == "Ethnic":
                    results[prop] = "".join(lazy_pinyin(value[:-1])).title()
                elif prop in [
                    "Date of Birth",
                    "Date of Enrollment",
                    "Update Date",
                    "Expected Graduation Date",
                    "Date of Leaving Institution",
                ]:
                    date = datetime.strptime(value, "%Y年%m月%d日")
                    results[prop] = date.strftime("%d %b %Y")
                elif prop == "Levels":
                    results[prop] = {
                        "本科": "Undergraduate",
                        "硕士研究生": "Master",
                        "博士研究生": "Doctoral",
                        "专科": "Junior college",
                    }.get(value, value)
                elif prop == "Form":
                    results[prop] = {"普通全日制": "Regular full-time", "全日制": "Full-time"}.get(
                        value, value
                    )
                elif prop == "Educational System":
                    results[prop] = f"{value.rstrip('年')} years"
                elif prop == "Type":
                    results[prop] = {"普通高等教育": "General higher education"}.get(value, value)
                elif prop == "School Status":
                    results[prop] = {
                        "在籍（注册学籍）": "Currently enrolled",
                        "在籍": "Currently enrolled",
                        "毕业": "Graduated",
                        "不在籍（毕业）": "Graduated",
                    }.get(value, value)
                else:
                    results[prop] = value
            else:
                results[prop] = None
        return results

    @classmethod
    def extract_info_from_pdf(cls, path):
        text = cls.extract_text_from_pdf(path)
        try:
            # pypdf may insert newlines between touching text objects. Reuse
            # their visual runs so split field values are not silently cut off.
            spans = text_origins(PdfReader(path).pages[0])
            text = "\n".join(span["text"] for span in spans)
        except Exception:
            # Inspection may still extract fields from an unsupported layout;
            # conversion independently validates every original text position.
            pass
        labels = {
            "Update Date": ("更新日期",),
            "Name": ("姓名",),
            "Gender": ("性别",),
            "Id Number": ("证件号码",),
            "Ethnic": ("民族",),
            "Date of Birth": ("出生日期",),
            "Institution": ("学校名称", "院校"),
            "Branch": ("分院",),
            "Levels": ("层次",),
            "Faculties": ("系所", "院系"),
            "Class": ("班级",),
            "Major": ("专业",),
            "Student Number": ("学号",),
            "Form": ("学习形式",),
            "Date of Enrollment": ("入学日期",),
            "Educational System": ("学制",),
            "Type": ("学历类别",),
            "School Status": ("学籍状态",),
            "Expected Graduation Date": ("预计毕业日期",),
            "Date of Leaving Institution": ("离校日期", "毕业日期"),
            "Verification Code": ("在线验证码",),
        }
        all_labels = "|".join(
            re.escape(label)
            for label in sorted(
                {label for alternatives in labels.values() for label in alternatives},
                key=len,
                reverse=True,
            )
        )
        patterns = {}
        for prop, alternatives in labels.items():
            label_pattern = "|".join(re.escape(label) for label in alternatives)
            patterns[prop] = re.compile(
                rf"(?<![\u4e00-\u9fff])(?:{label_pattern})[：:]*\s*"
                rf"(?!(?:{all_labels})[：:]*(?:\s|$))([^\s]+)"
            )
        info = cls.extract_info(patterns, text)
        # Exact names only: similar institution names must never be conflated.
        info["Institution"] = UNIVERSITY_NAMES.get(info["Institution"], info["Institution"])
        # Unknown major and department names retain their source wording.
        translations = {
            "人工智能": "Artificial Intelligence",
            "信息科学技术学院": "School of Information Science and Technology",
        }
        for key in ["Major", "Faculties"]:
            info[key] = translations.get(info[key], info[key])
        return info

    @classmethod
    def convert_to_pdf(cls, path, output_path, overrides=None):
        output_path = Path(output_path)
        info = cls.extract_info_from_pdf(path)
        required_fields = ["Update Date", "Name", "Institution"]
        missing_fields = [key for key in required_fields if not info.get(key)]
        if missing_fields:
            raise ConversionError(
                "unsupported_report",
                f"required fields missing: {', '.join(missing_fields)}",
            )
        overrides = overrides or {}
        for key, value in overrides.items():
            if key not in {"Institution", "Branch", "Major", "Faculties", "Name"}:
                raise ConversionError("invalid_translation", f"unsupported override field: {key}")
            if not value or len(value) > 200 or any(ord(char) < 32 for char in value):
                raise ConversionError(
                    "invalid_translation",
                    f"invalid override value for {key}: length={len(value)}",
                )
            if re.search(r"[\u4e00-\u9fff]", value):
                raise ConversionError(
                    "invalid_translation", f"override for {key} contains Chinese characters"
                )
            info[key] = value

        # Never invent official institution, major or department names.
        untranslated_fields = [
            key for key, value in info.items() if re.search(r"[\u4e00-\u9fff]", value or "")
        ]
        if untranslated_fields:
            field_status = []
            for key, label in [
                ("Institution", "学校"),
                ("Branch", "分院"),
                ("Major", "专业"),
                ("Faculties", "院系"),
                ("Name", "姓名"),
            ]:
                value = info.get(key)
                if not value:
                    state = "not_present"
                    display_value = ""
                elif re.search(r"[\u4e00-\u9fff]", value):
                    state = "needs_input"
                    display_value = value
                else:
                    state = "recognized"
                    display_value = value
                display_value = str(display_value)
                if len(display_value) > 160:
                    display_value = display_value[:157] + "..."
                field_status.append(
                    {
                        "key": key,
                        "label": label,
                        "state": state,
                        "value": display_value,
                    }
                )
            raise ConversionError(
                "missing_translation",
                f"untranslated fields: {', '.join(untranslated_fields)}",
                {"translation_fields": field_status},
            )
        writer = PdfWriter(clone_from=path)
        if len(writer.pages) != 1:
            raise ConversionError(
                "unsupported_report", f"expected exactly 1 page, found {len(writer.pages)}"
            )
        page = writer.pages[0]
        # Translation keeps artwork and trusted verification links, not active PDF actions.
        for key in ["/OpenAction", "/AA", "/Names", "/AcroForm"]:
            writer.root_object.pop(key, None)
        page.pop("/AA", None)
        links = []
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            action = annotation.get("/A", {})
            if hasattr(action, "get_object"):
                action = action.get_object()
            address = urlparse(str(action.get("/URI", "")))
            host = address.hostname or ""
            if (
                annotation.get("/Subtype") == "/Link"
                and action.get("/S") == "/URI"
                and address.scheme == "https"
                and (host == "chsi.com.cn" or host.endswith(".chsi.com.cn"))
            ):
                annotation.pop("/AA", None)
                links.append(reference)
        page[NameObject("/Annots")] = ArrayObject(links)
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if page.rotation or abs(width - 595) > 3 or abs(height - 842) > 3:
            raise ConversionError(
                "unsupported_report",
                "expected unrotated A4 page: "
                f"width={width:.1f}, height={height:.1f}, rotation={page.rotation}",
            )
        try:
            spans = text_origins(page)
        except Exception as error:
            raise ConversionError(
                "unsupported_report",
                f"text layout probe failed: {type(error).__name__}: {error}",
            ) from None
        labels = [span for span in spans if span["text"] in LABELS and span["x"] < 130]
        title_found = any(s["text"] == "教育部学籍在线验证报告" for s in spans)
        if not labels or not title_found:
            detected_labels = (
                ", ".join(sorted({LABELS[span["text"]][0] for span in labels})) or "none"
            )
            raise ConversionError(
                "unsupported_report",
                "report markers not found: "
                f"title={title_found}, labels={len(labels)}, detected_labels={detected_labels}",
            )

        code_label = next((s for s in spans if s["text"] == "在线验证码"), None)
        code_value = next((s for s in spans if s["text"] == info["Verification Code"]), None)
        if code_label and code_value:
            original_x = code_value["x"]
            code_value["x"] = adjacent_text_x(
                VERIFICATION_LABEL, code_label["size"], code_label["x"], original_x
            )
            for reference in page.get("/Annots", []):
                annotation = reference.get_object()
                rect = annotation.get("/Rect")
                if (
                    annotation.get("/Subtype") == "/Link"
                    and rect
                    and abs(float(rect[0]) - original_x) < 1
                    and float(rect[1]) <= code_value["y"] <= float(rect[3])
                ):
                    font = "Helvetica-Bold" if code_value["bold"] else "Helvetica"
                    annotation[NameObject("/Rect")] = RectangleObject(
                        [
                            code_value["x"],
                            rect[1],
                            code_value["x"]
                            + stringWidth(code_value["text"], font, code_value["size"]),
                            rect[3],
                        ]
                    )

        overlay = BytesIO()
        drawing = canvas.Canvas(overlay, pagesize=(width, height), pageCompression=1)

        def draw(text, x, y, size, available, color=(0, 0, 0), bold=False, centered=False):
            if not text:
                return
            try:
                text.encode("cp1252")
            except UnicodeEncodeError:
                raise ConversionError(
                    "invalid_translation",
                    f"translated text is not cp1252 encodable: chars={len(text)}",
                ) from None
            font = "Helvetica-Bold" if bold else "Helvetica"
            text_width = stringWidth(text, font, size)
            size *= min(1, available / max(text_width, 1))
            if size < 6:
                raise ConversionError(
                    "translation_too_long",
                    f"translated text cannot fit at minimum font size: chars={len(text)}",
                )
            drawing.setFillColorRGB(*color)
            drawing.setFont(font, size)
            if centered:
                drawing.drawCentredString(x, y, text)
            else:
                drawing.drawString(x, y, text)

        for span in spans:
            text, x, y, size = (span[key] for key in ["text", "x", "y", "size"])
            if span in labels:
                english, _key = LABELS[text]
                draw(english, x, y, size, 112, color=span["color"])
            elif text == "教育部学籍在线验证报告":
                draw(
                    "Online Verification Report of Student Record",
                    width / 2,
                    y,
                    size,
                    width - 110,
                    bold=True,
                    centered=True,
                )
            elif text.startswith("更新日期"):
                draw(
                    "Updated: " + info["Update Date"],
                    width / 2,
                    y,
                    size,
                    width - 120,
                    color=span["color"],
                    centered=True,
                )
            elif text in FOOTNOTES:
                draw(FOOTNOTES[text], x, y, size, width - x - 60, bold=text.startswith("注意事项"))
            elif text == "在线验证码":
                available = (code_value["x"] - x - 2) if code_value else width - x - 60
                draw(VERIFICATION_LABEL, x, y, size, available)
            elif text.startswith("①") and "https://" in text:
                url = text[text.index("https://") :]
                draw("1. Verify online: " + url, x, y, size, width - x - 60)
            elif text.startswith("②") and "二维码" in text:
                draw("2. Scan the QR code with the CHSI App to verify.", x, y, size, width - x - 60)
            elif any(abs(label["y"] - y) < 2 and x > label["x"] + 60 for label in labels):
                label = next(label for label in labels if abs(label["y"] - y) < 2)
                _english, key = LABELS[label["text"]]
                value = info.get(key) if key else None
                if value is None and re.search(r"[\u4e00-\u9fff]", text):
                    raise ConversionError(
                        "unsupported_report",
                        f"no value mapping for label={_english}, y={y:.1f}",
                    )
                draw(value or text, x, y, size, width - x - (145 if y > height * 0.65 else 60))
            elif re.search(r"[\u4e00-\u9fff]", text):
                raise ConversionError(
                    "unsupported_report",
                    "unmapped Chinese text: "
                    f"length={len(text)}, x={x:.1f}, y={y:.1f}, size={size:.1f}",
                )
            else:
                draw(text, x, y, size, width - x - 50, color=span["color"], bold=span["bold"])

        drawing.save()
        content = ContentStream(page.get_contents(), writer)
        content.operations = [
            (args, op) for args, op in content.operations if op not in {b"Tj", b"TJ", b"'", b'"'}
        ]
        page.replace_contents(content)
        page.merge_page(PdfReader(overlay).pages[0])
        writer.metadata = None
        writer.add_metadata(
            {
                "/Title": "English translation of student record verification report",
                "/Subject": "Unofficial translation; verify with the original CHSI report.",
            }
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer.write(output_path)
