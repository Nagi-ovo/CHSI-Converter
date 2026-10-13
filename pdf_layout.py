"""Read the text origins of CHSI PDFs, including adjacent runs in one text block."""

from reportlab.pdfbase.pdfmetrics import stringWidth


def adjacent_text_x(label, label_size, label_x, original_value_x, gap=4):
    """Keep a label on one line and leave a gap before its value."""
    return max(original_value_x, label_x + stringWidth(label, "Helvetica", label_size) + gap)


def text_origins(page):
    origins = []
    font = None
    size = 0
    advance = spacing = word_spacing = 0
    scale = 1
    color, rendering = (0, 0, 0), 0
    graphics = []

    def width(raw):
        if not raw or not font:
            return 0
        data = raw.original_bytes if hasattr(raw, "original_bytes") else bytes(raw)
        if "/DescendantFonts" in font:
            descendant = font["/DescendantFonts"][0].get_object()
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

    def before(op, args, cm, tm):
        nonlocal font, size, advance, spacing, word_spacing, scale, color, rendering
        if op in {b"BT", b"Tm", b"Td", b"TD", b"T*"}:
            advance = 0
        elif op == b"Tf":
            font = page["/Resources"]["/Font"][args[0]].get_object()
            size = float(args[1])
        elif op == b"Tc":
            spacing = float(args[0])
        elif op == b"Tw":
            word_spacing = float(args[0])
        elif op == b"Tz":
            scale = float(args[0]) / 100
        elif op == b"q":
            graphics.append((color, rendering))
        elif op == b"Q" and graphics:
            color, rendering = graphics.pop()
        elif op == b"g":
            color = (float(args[0]),) * 3
        elif op == b"rg":
            color = tuple(float(value) for value in args)
        elif op == b"Tr":
            rendering = int(args[0])
        elif op == b"Tj" and args[0]:
            if len(origins) >= 1000:
                raise ValueError("Too many text runs")
            x, y = tm[4] + advance * tm[0], tm[5] + advance * tm[1]
            origins.append(
                (
                    x * cm[0] + y * cm[2] + cm[4],
                    x * cm[1] + y * cm[3] + cm[5],
                    color,
                    rendering == 2,
                )
            )
            advance += width(args[0]) * scale
        elif op in {b"TJ", b"'", b'"'}:
            raise ValueError("Unsupported text positioning")

    spans = []

    def collect(text, _cm, _tm, _font, size):
        if text.strip():
            spans.append({"text": text.strip(), "size": size})

    page.extract_text(visitor_operand_before=before, visitor_text=collect)
    if len(origins) != len(spans):
        raise ValueError("Ambiguous text positioning")
    for span, (x, y, color, bold) in zip(spans, origins):
        span.update(x=x, y=y, color=color, bold=bold)
    return spans
