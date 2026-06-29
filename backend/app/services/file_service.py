import io
import json
import re


def txt_to_tiptap(text: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    content = [{"type": "paragraph", "content": [{"type": "text", "text": p}]} for p in paragraphs]
    if not content:
        content = [{"type": "paragraph"}]
    return json.dumps({"type": "doc", "content": content})


def md_to_tiptap(text: str) -> str:
    lines = text.splitlines()
    nodes = []
    i = 0
    while i < len(lines):
        line = lines[i]

        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            level = min(len(heading_match.group(1)), 3)
            nodes.append({"type": "heading", "attrs": {"level": level}, "content": _parse_inline(heading_match.group(2).strip())})
            i += 1
            continue

        if re.match(r"^[-*+]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                item_text = re.sub(r"^[-*+]\s+", "", lines[i])
                items.append({"type": "listItem", "content": [{"type": "paragraph", "content": _parse_inline(item_text)}]})
                i += 1
            nodes.append({"type": "bulletList", "content": items})
            continue

        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i])
                items.append({"type": "listItem", "content": [{"type": "paragraph", "content": _parse_inline(item_text)}]})
                i += 1
            nodes.append({"type": "orderedList", "attrs": {"start": 1}, "content": items})
            continue

        if not line.strip():
            i += 1
            continue

        para_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|[-*+]\s|\d+\.\s)", lines[i]):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            nodes.append({"type": "paragraph", "content": _parse_inline(" ".join(para_lines))})

    if not nodes:
        nodes = [{"type": "paragraph"}]
    return json.dumps({"type": "doc", "content": nodes})


def _parse_inline(text: str) -> list:
    # handles **bold** and *italic* — matches longest token first
    result = []
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*)")
    last = 0
    for m in pattern.finditer(text):
        if m.start() > last:
            result.append({"type": "text", "text": text[last:m.start()]})
        if m.group(0).startswith("**"):
            result.append({"type": "text", "marks": [{"type": "bold"}], "text": m.group(2)})
        else:
            result.append({"type": "text", "marks": [{"type": "italic"}], "text": m.group(3)})
        last = m.end()
    if last < len(text):
        result.append({"type": "text", "text": text[last:]})
    return result or [{"type": "text", "text": ""}]


def docx_to_tiptap(content: bytes) -> str:
    from docx import Document as DocxDocument
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = DocxDocument(io.BytesIO(content))
    nodes = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style = para.style.name if para.style else ""

        if style.startswith("Heading"):
            try:
                level = min(int(style.split()[-1]), 3)
            except (ValueError, IndexError):
                level = 1
            nodes.append({"type": "heading", "attrs": {"level": level}, "content": _runs_to_inline(para.runs)})

        elif style in ("List Bullet", "List Bullet 2", "List Bullet 3"):
            nodes.append({"type": "bulletList", "content": [
                {"type": "listItem", "content": [{"type": "paragraph", "content": _runs_to_inline(para.runs)}]}
            ]})

        elif style in ("List Number", "List Number 2", "List Number 3"):
            nodes.append({"type": "orderedList", "attrs": {"start": 1}, "content": [
                {"type": "listItem", "content": [{"type": "paragraph", "content": _runs_to_inline(para.runs)}]}
            ]})

        else:
            nodes.append({"type": "paragraph", "content": _runs_to_inline(para.runs)})

    if not nodes:
        nodes = [{"type": "paragraph"}]
    return json.dumps({"type": "doc", "content": nodes})


def _runs_to_inline(runs) -> list:
    result = []
    for run in runs:
        if not run.text:
            continue
        marks = []
        if run.bold:
            marks.append({"type": "bold"})
        if run.italic:
            marks.append({"type": "italic"})
        if run.underline:
            marks.append({"type": "underline"})
        node = {"type": "text", "text": run.text}
        if marks:
            node["marks"] = marks
        result.append(node)
    return result or [{"type": "text", "text": ""}]


def file_to_tiptap(filename: str, content: bytes) -> str:
    if filename.endswith(".docx"):
        return docx_to_tiptap(content)
    text = content.decode("utf-8", errors="replace")
    if filename.endswith(".md"):
        return md_to_tiptap(text)
    return txt_to_tiptap(text)
