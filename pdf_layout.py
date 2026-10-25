"""Read the text origins of CHSI PDFs, including adjacent runs in one text block."""

from copy import copy

from pypdf.generic import ByteStringObject, ContentStream, NameObject, NumberObject
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import stringWidth


def adjacent_text_x(label, label_size, label_x, original_value_x, gap=4):
    """Keep a label on one line and leave a gap before its value."""
    return max(original_value_x, label_x + stringWidth(label, "Helvetica", label_size) + gap)


def text_origins(page):
    runs = []
    font_name = None
    font = None
    size = 0
    advance = spacing = word_spacing = leading = 0
    scale = 1
    color, rendering = (0, 0, 0), 0
    graphics = []
    standard_cid = UnicodeCIDFont("STSong-Light")
    cid_widths = {}

    def width(raw, font, size, spacing, word_spacing):
        if not raw or not font:
            return 0
        data = raw.original_bytes if hasattr(raw, "original_bytes") else bytes(raw)
        if "/DescendantFonts" in font:
            descendant = font["/DescendantFonts"][0].get_object()
            if id(font) not in cid_widths:
                widths, items = {}, descendant.get("/W", [])
                i = entries = 0
                while i < len(items):
                    start, second = int(items[i]), items[i + 1]
                    if isinstance(second, list):
                        end = start + len(second) - 1
                        entries += len(second)
                        if start < 0 or end > 65535 or entries > 65536:
                            raise ValueError("Invalid CID width range")
                        widths.update(
                            (start + offset, float(value)) for offset, value in enumerate(second)
                        )
                        i += 2
                    else:
                        end = int(second)
                        entries += end - start + 1
                        if not 0 <= start <= end <= 65535 or entries > 65536:
                            raise ValueError("Invalid CID width range")
                        widths.update(
                            (code, float(items[i + 2])) for code in range(start, int(second) + 1)
                        )
                        i += 3
                cid_widths[id(font)] = widths
            widths = cid_widths[id(font)]
            # UCS2 code points are not CIDs: the standard CJK CMap remaps ASCII.
            # ReportLab supplies the standard STSong Unicode metrics already.
            if (
                font.get("/BaseFont") == "/STSong-Light"
                and font.get("/Encoding") == "/UniGB-UCS2-H"
            ):
                return standard_cid.stringWidth(data.decode("utf-16-be"), size) + spacing * (
                    len(data) // 2
                )
            codes = [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)]
            return sum(
                widths.get(code, float(descendant.get("/DW", 1000))) for code in codes
            ) * size / 1000 + spacing * len(codes)
        first = int(font.get("/FirstChar", 0))
        widths = font.get("/Widths")
        if widths:
            glyph_width = sum(float(widths[code - first]) for code in data) * size / 1000
        else:
            name = str(font.get("/BaseFont", "/Helvetica")).lstrip("/").split("+")[-1]
            glyph_width = stringWidth(data.decode("latin1"), name, size)
        return glyph_width + spacing * len(data) + word_spacing * data.count(b" ")

    def show(raw, cm, tm):
        nonlocal advance
        if not raw:
            return
        if len(runs) >= 1000:
            raise ValueError("Too many text runs")
        if not font_name:
            raise ValueError("Missing text font")
        # The output writer only supports horizontal report text.
        # Refuse other geometry rather than silently move or resize its text.
        if any(abs(value) > 0.001 for value in (tm[1], tm[2], cm[1], cm[2])):
            raise ValueError("Unsupported text rotation")
        x, y = tm[4] + advance * tm[0], tm[5] + advance * tm[1]
        run_width = width(raw, font, size, spacing, word_spacing) * scale
        runs.append(
            {
                "raw": ByteStringObject(
                    raw.original_bytes if hasattr(raw, "original_bytes") else bytes(raw)
                ),
                "font": font_name,
                "size": size,
                "x": x * cm[0] + y * cm[2] + cm[4],
                "y": x * cm[1] + y * cm[3] + cm[5],
                "end": (x + run_width * tm[0]) * cm[0] + y * cm[2] + cm[4],
                "color": color,
                "bold": rendering == 2,
                "metrics": (font, size, spacing, word_spacing),
                "width_scale": scale * tm[0] * cm[0],
            }
        )
        advance += run_width

    def before(op, args, cm, tm):
        nonlocal font, font_name, size, advance, spacing, word_spacing, scale
        nonlocal color, rendering, leading
        if op in {b"BT", b"Tm", b"Td", b"TD", b"T*"}:
            advance = 0
            if op == b"TD":
                leading = -float(args[1])
        elif op == b"TL":
            leading = float(args[0])
        elif op == b"Tf":
            font_name = args[0]
            font = page["/Resources"]["/Font"][font_name].get_object()
            size = float(args[1])
        elif op == b"Tc":
            spacing = float(args[0])
        elif op == b"Tw":
            word_spacing = float(args[0])
        elif op == b"Tz":
            scale = float(args[0]) / 100
        elif op == b"q":
            graphics.append(
                (font, font_name, size, spacing, word_spacing, scale, color, rendering, leading)
            )
        elif op == b"Q" and graphics:
            font, font_name, size, spacing, word_spacing, scale, color, rendering, leading = (
                graphics.pop()
            )
        elif op == b"g":
            color = (float(args[0]),) * 3
        elif op == b"rg":
            color = tuple(float(value) for value in args)
        elif op == b"Tr":
            rendering = int(args[0])
        elif op == b"Tj":
            show(args[0], cm, tm)
        elif op == b"TJ":
            for item in args[0]:
                if isinstance(item, (str, bytes)):
                    show(item, cm, tm)
                else:
                    advance -= float(item) * size * scale / 1000
        elif op in {b"'", b'"'}:
            if op == b'"':
                word_spacing, spacing = float(args[0]), float(args[1])
            advance = 0
            next_line = list(tm)
            next_line[4] -= leading * tm[2]
            next_line[5] -= leading * tm[3]
            show(args[-1], cm, next_line)

    page.extract_text(visitor_operand_before=before)
    if not runs:
        return []

    # visitor_text batches adjacent Tj/TJ runs and may add whitespace/newlines.
    # Decode isolated copies instead, using pypdf's public font/CMap handling.
    # This temporary page never replaces or modifies the original page content.
    decoder = copy(page)
    content = ContentStream(None, None)
    content.operations = [
        operation
        for run in runs
        for operation in [
            ([], b"BT"),
            ([run["font"], NumberObject(10)], b"Tf"),
            ([run["raw"]], b"Tj"),
            ([], b"ET"),
        ]
    ]
    decoder[NameObject("/Contents")] = content
    index = -1
    decoded = [""] * len(runs)

    def decoding_run(op, _args, _cm, _tm):
        nonlocal index
        if op == b"BT":
            index += 1

    def collect(text, _cm, _tm, _font, _size):
        if text:
            if not 0 <= index < len(runs):
                raise ValueError("Ambiguous text decoding")
            decoded[index] += text

    decoder.extract_text(visitor_operand_before=decoding_run, visitor_text=collect)
    spans = []
    previous = None
    for run, text in zip(runs, decoded):
        if not text.strip():
            previous = None
            continue
        leading_space = len(text) - len(text.lstrip())
        if leading_space:
            # Trimming a visible run must also move its origin past the spaces.
            # Refuse ambiguous multicharacter mappings instead of guessing bytes.
            byte_count = 2 if "/DescendantFonts" in run["metrics"][0] else 1
            if len(run["raw"]) != len(text) * byte_count:
                raise ValueError("Ambiguous leading whitespace")
            prefix = run["raw"][: leading_space * byte_count]
            run["x"] += width(prefix, *run["metrics"]) * run["width_scale"]
            previous = None
        # Merge only touching pieces in the same style and on the same baseline.
        # Large gaps (notably label/value columns) remain independent spans.
        if (
            previous is not None
            and abs(run["y"] - previous["y"]) < 0.1
            and -1.01 <= run["x"] - previous["end"] <= 1
            and all(run[key] == previous[key] for key in ("font", "size", "color", "bold"))
        ):
            spans[-1]["text"] += text.strip()
        else:
            spans.append(
                {key: run[key] for key in ("x", "y", "size", "color", "bold")}
                | {"text": text.strip()}
            )
        previous = run if text == text.rstrip() else None
    return spans
