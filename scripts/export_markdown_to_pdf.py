"""Export Markdown documentation to a styled PDF using Matplotlib."""
from __future__ import annotations

import textwrap

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch
from matplotlib.table import Table as MplTable


PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0
MARGIN_LEFT_IN = 0.75
MARGIN_RIGHT_IN = 0.75
MARGIN_TOP_IN = 0.85
MARGIN_BOTTOM_IN = 0.85
BACKGROUND_COLOR = "#F9FAFB"


@dataclass
class CodeBlock:
    language: str | None
    title: str | None
    lines: List[str]


@dataclass
class TableBlock:
    rows: List[List[str]]


@dataclass
class Element:
    type: str
    content: str | List[str] | CodeBlock | TableBlock
    level: int | None = None
    ordered: bool | None = None


class PDFBuilder:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.pdf = PdfPages(str(output_path))
        self.fig = None
        self.ax = None
        self.cursor_y = 0.0
        self._new_page()

    @property
    def usable_width_in(self) -> float:
        return PAGE_WIDTH_IN - MARGIN_LEFT_IN - MARGIN_RIGHT_IN

    @property
    def usable_height_in(self) -> float:
        return PAGE_HEIGHT_IN - MARGIN_TOP_IN - MARGIN_BOTTOM_IN

    def _new_page(self) -> None:
        if self.fig is not None:
            self.pdf.savefig(self.fig)
            plt.close(self.fig)
        self.fig, self.ax = plt.subplots(figsize=(PAGE_WIDTH_IN, PAGE_HEIGHT_IN))
        self.fig.patch.set_facecolor(BACKGROUND_COLOR)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")
        self.cursor_y = 1 - (MARGIN_TOP_IN / PAGE_HEIGHT_IN)

    def _font(self, size: float, weight: str = 'normal', family: str = 'DejaVu Sans', style: str | None = None) -> FontProperties:
        return FontProperties(family=family, size=size, weight=weight, style=style)

    def _line_height(self, font_size: float, spacing: float = 1.2) -> float:
        return (font_size / 72.0) / PAGE_HEIGHT_IN * spacing

    def _wrap_text(self, text: str, font: FontProperties) -> List[str]:
        if not text:
            return [""]
        max_chars = max(20, int(self.usable_width_in * 72 / (font.get_size_in_points() * 0.6)))
        wrapped = textwrap.wrap(text, width=max_chars)
        return wrapped or [text]

    def _ensure_space(self, height: float) -> None:
        available = self.cursor_y - (MARGIN_BOTTOM_IN / PAGE_HEIGHT_IN)
        if available < height:
            self._new_page()

    def add_heading(self, text: str, level: int) -> None:
        size = {1: 20, 2: 16, 3: 13}.get(level, 12)
        weight = "bold" if level <= 2 else "semibold"
        color = {1: "#1F2937", 2: "#1F2937", 3: "#334155"}.get(level, "#111827")
        font = self._font(size=size, weight=weight)
        lines = self._wrap_text(text, font)
        total_height = len(lines) * self._line_height(size) + self._line_height(8)
        self._ensure_space(total_height)
        y = self.cursor_y
        x = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        for line in lines:
            self.ax.text(x, y, line, fontproperties=font, color=color, transform=self.fig.transFigure)
            y -= self._line_height(size)
        self.cursor_y = y - self._line_height(8)

    def add_paragraph(self, text: str) -> None:
        font = self._font(size=11)
        lines = self._wrap_text(text, font)
        height = len(lines) * self._line_height(11) + self._line_height(4)
        self._ensure_space(height)
        y = self.cursor_y
        x = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        for line in lines:
            self.ax.text(x, y, line, fontproperties=font, color="#111827", transform=self.fig.transFigure)
            y -= self._line_height(11)
        self.cursor_y = y - self._line_height(4)

    def add_blockquote(self, text: str) -> None:
        font = self._font(size=11, style='italic')
        lines = self._wrap_text(text, font)
        padding = self._line_height(11)
        height = len(lines) * self._line_height(11) + padding * 2
        self._ensure_space(height)
        x0 = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        width = self.usable_width_in / PAGE_WIDTH_IN
        y0 = self.cursor_y
        rect = FancyBboxPatch(
            (x0 - 0.01, y0 - height + padding / 2),
            width + 0.02,
            height,
            boxstyle="round,pad=0.02",
            linewidth=0.5,
            facecolor="#EEF2FF",
            edgecolor="#C7D2FE",
            transform=self.fig.transFigure,
        )
        self.ax.add_patch(rect)
        y = y0 - padding
        for line in lines:
            self.ax.text(
                x0 + 0.01,
                y,
                line,
                fontproperties=font,
                color="#4B5563",
                transform=self.fig.transFigure,
            )
            y -= self._line_height(11)
        self.cursor_y = (y - padding / 2)

    def add_list(self, items: List[str], ordered: bool) -> None:
        font = self._font(size=11)
        bullet_prefix = "•"
        for idx, item in enumerate(items, start=1):
            prefix = f"{idx}." if ordered else bullet_prefix
            line_text = f"{prefix} {item}"
            lines = self._wrap_text(line_text, font)
            height = len(lines) * self._line_height(11)
            self._ensure_space(height + self._line_height(6))
            y = self.cursor_y
            for i, line in enumerate(lines):
                if i == 0:
                    display = line
                else:
                    display = f"    {line}"
                self.ax.text(
                    MARGIN_LEFT_IN / PAGE_WIDTH_IN,
                    y,
                    display,
                    fontproperties=font,
                    color="#111827",
                    transform=self.fig.transFigure,
                )
                y -= self._line_height(11)
            self.cursor_y = y
        self.cursor_y -= self._line_height(6)

    def add_code_block(self, block: CodeBlock) -> None:
        font = self._font(size=9, family="DejaVu Sans Mono")
        lines = block.lines or [""]
        line_height = self._line_height(9, spacing=1.3)
        padding = line_height * 1.5
        height = len(lines) * line_height + padding
        self._ensure_space(height + self._line_height(6))
        x = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        width = self.usable_width_in / PAGE_WIDTH_IN
        y_top = self.cursor_y
        rect = FancyBboxPatch(
            (x - 0.005, y_top - height + padding / 2),
            width + 0.01,
            height,
            boxstyle="round,pad=0.02",
            linewidth=0,
            facecolor="#1F2933",
            transform=self.fig.transFigure,
        )
        self.ax.add_patch(rect)
        y = y_top - padding / 2
        for line in lines:
            self.ax.text(
                x + 0.01,
                y,
                line,
                fontproperties=font,
                color="#E0F2FE",
                transform=self.fig.transFigure,
            )
            y -= line_height
        self.cursor_y = y - self._line_height(6)
        if block.title:
            caption_font = self._font(size=9)
            caption_height = self._line_height(9)
            self._ensure_space(caption_height)
            self.ax.text(
                0.5,
                self.cursor_y,
                block.title,
                fontproperties=caption_font,
                color="#6B7280",
                ha="center",
                transform=self.fig.transFigure,
            )
            self.cursor_y -= self._line_height(10)

    def add_table(self, table_block: TableBlock) -> None:
        rows = table_block.rows
        if not rows:
            return
        n_rows = len(rows)
        cell_height = self._line_height(10, spacing=1.6)
        height = n_rows * cell_height + self._line_height(8)
        self._ensure_space(height)
        x = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        width = self.usable_width_in / PAGE_WIDTH_IN
        table = MplTable(self.ax, bbox=[x, self.cursor_y - height + self._line_height(4), width, height])
        header_color = "#DBEAFE"
        header_text = "#1E3A8A"
        cell_bg = "#F8FAFC"
        border_color = "#93C5FD"
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                facecolor = header_color if row_idx == 0 else cell_bg
                text_color = header_text if row_idx == 0 else "#111827"
                cell_obj = table.add_cell(
                    row=row_idx,
                    col=col_idx,
                    width=width / len(row),
                    height=cell_height,
                    text=cell,
                    loc="left",
                    facecolor=facecolor,
                    edgecolor=border_color,
                )
                cell_obj.PAD = 0.18
                cell_obj.get_text().set_fontproperties(self._font(size=10 if row_idx == 0 else 9, weight='bold' if row_idx == 0 else 'normal'))
                cell_obj.get_text().set_color(text_color)
        self.ax.add_table(table)
        self.cursor_y -= height

    def add_horizontal_rule(self) -> None:
        self._ensure_space(self._line_height(4))
        x0 = MARGIN_LEFT_IN / PAGE_WIDTH_IN
        x1 = 1 - MARGIN_RIGHT_IN / PAGE_WIDTH_IN
        y = self.cursor_y
        self.ax.plot([x0, x1], [y, y], color="#CBD5F5", linewidth=1, transform=self.fig.transFigure)
        self.cursor_y -= self._line_height(6)

    def close(self) -> None:
        if self.fig is not None:
            self.pdf.savefig(self.fig)
            plt.close(self.fig)
        self.pdf.close()



def strip_markup(text: str) -> str:
    # For PDF rendering we keep the raw text; markup already described in headings
    return re.sub(r"[*_`]+", "", text)


def parse_markdown(markdown: str) -> List[Element]:
    elements: List[Element] = []
    lines = markdown.splitlines()
    code_block: CodeBlock | None = None
    table_buffer: List[List[str]] = []
    list_buffer: List[str] = []
    ordered_buffer: List[str] = []

    def flush_lists() -> None:
        nonlocal list_buffer, ordered_buffer
        if list_buffer:
            elements.append(Element(type="list", content=list_buffer, ordered=False))
            list_buffer = []
        if ordered_buffer:
            elements.append(Element(type="list", content=ordered_buffer, ordered=True))
            ordered_buffer = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            elements.append(Element(type="table", content=TableBlock(rows=table_buffer)))
            table_buffer = []

    for line in lines:
        stripped = line.rstrip()
        if code_block is not None:
            if stripped.startswith("```"):
                elements.append(Element(type="code", content=code_block))
                code_block = None
            else:
                code_block.lines.append(stripped)
            continue

        if stripped.startswith("```"):
            flush_lists()
            flush_table()
            info = stripped.strip("`")
            language = None
            title = None
            if info:
                match = re.search(r"title=\"([^\"]+)\"", info)
                if match:
                    title = match.group(1)
                parts = info.split()
                if parts:
                    language = parts[0] if not parts[0].startswith("title=") else None
            code_block = CodeBlock(language=language, title=title, lines=[])
            continue

        if not stripped:
            flush_lists()
            flush_table()
            elements.append(Element(type="spacer", content=""))
            continue

        if stripped.startswith("---") and set(stripped) == {"-"}:
            flush_lists()
            flush_table()
            elements.append(Element(type="rule", content=""))
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)", stripped)
        if heading:
            flush_lists()
            flush_table()
            level = len(heading.group(1))
            elements.append(Element(type="heading", content=strip_markup(heading.group(2)), level=level))
            continue

        if stripped.startswith(">"):
            flush_lists()
            flush_table()
            elements.append(Element(type="blockquote", content=strip_markup(stripped.lstrip("> "))))
            continue

        bullet = re.match(r"^[-*]\s+(.*)", stripped)
        if bullet:
            list_buffer.append(strip_markup(bullet.group(1)))
            continue

        ordered = re.match(r"^\d+\.\s+(.*)", stripped)
        if ordered:
            ordered_buffer.append(strip_markup(ordered.group(1)))
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_lists()
            cells = [strip_markup(cell.strip()) for cell in stripped.strip("|").split("|")]
            table_buffer.append(cells)
            continue

        flush_table()
        flush_lists()
        elements.append(Element(type="paragraph", content=strip_markup(stripped)))

    flush_lists()
    flush_table()
    if code_block is not None:
        elements.append(Element(type="code", content=code_block))
    return elements


def render_markdown_to_pdf(markdown: str, output_path: Path) -> None:
    builder = PDFBuilder(output_path)
    for element in parse_markdown(markdown):
        if element.type == "heading":
            builder.add_heading(str(element.content), level=element.level or 1)
        elif element.type == "paragraph":
            builder.add_paragraph(str(element.content))
        elif element.type == "blockquote":
            builder.add_blockquote(str(element.content))
        elif element.type == "list":
            builder.add_list(list(element.content), ordered=bool(element.ordered))
        elif element.type == "code":
            builder.add_code_block(element.content)  # type: ignore[arg-type]
        elif element.type == "table":
            builder.add_table(element.content)  # type: ignore[arg-type]
        elif element.type == "rule":
            builder.add_horizontal_rule()
        elif element.type == "spacer":
            builder.cursor_y -= builder._line_height(6)
    builder.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Markdown documentation to a PDF file.")
    parser.add_argument("source", type=Path, help="Markdown file to export.")
    parser.add_argument("--output", type=Path, help="Optional output PDF path.")
    args = parser.parse_args()

    if not args.source.exists():
        raise SystemExit(f"Source file not found: {args.source}")

    output = args.output or args.source.with_suffix(".pdf")
    markdown = args.source.read_text(encoding="utf-8")
    render_markdown_to_pdf(markdown, output)
    print(f"Exported {args.source} -> {output}")


if __name__ == "__main__":
    main()
