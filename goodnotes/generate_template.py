#!/usr/bin/env python3
"""Generate a GoodNotes-ready A4 PDF notebook for 高三 English class progress.

Classroom structure:
  - Every lesson: vocab dictation + grammar
  - Lesson 1: orientation
  - Lesson 2, 4, 6...: reading
  - Lesson 3, 5, 7...: writing
"""

from __future__ import annotations

import argparse
import os
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4
M = 30.0
CONTENT_W = PAGE_W - 2 * M

PAPER = HexColor("#FAF6F1")
CARD = HexColor("#FFFCFA")
INK = HexColor("#4A433E")
INK_SOFT = HexColor("#8A8178")
INK_FAINT = HexColor("#B4AAA2")
LINE = HexColor("#E4D8D1")
ACCENT = HexColor("#C9A39C")
ACCENT_SOFT = HexColor("#F4E8E4")
ROSE = HexColor("#E8C4BE")
SAGE = HexColor("#C5D5C8")
SAGE_SOFT = HexColor("#E8F0E9")
SAGE_INK = HexColor("#4F6A56")
BLUE = HexColor("#C5D4E0")
BLUE_SOFT = HexColor("#E6EEF4")
BLUE_INK = HexColor("#4A6174")
ROSE_INK = HexColor("#8F6863")
HEADER_RULE = HexColor("#E6D5CF")

KIND = {
    "intro": {
        "label": "导学课",
        "chip": ACCENT_SOFT,
        "ink": ROSE_INK,
        "bar": ACCENT,
        "third_title": "学情与学期目标",
        "third_hint": "本学期弱项 / 目标分数 / 听课约定（留空填写）",
    },
    "reading": {
        "label": "阅读课",
        "chip": SAGE_SOFT,
        "ink": SAGE_INK,
        "bar": SAGE,
        "third_title": "阅读",
        "third_hint": "篇章来源、题型、错因均可直接写在下方横线里",
    },
    "writing": {
        "label": "写作课",
        "chip": BLUE_SOFT,
        "ink": BLUE_INK,
        "bar": BLUE,
        "third_title": "写作",
        "third_hint": "题目、体裁、提纲、好词好句均可直接写在下方横线里",
    },
}

FONT = "CN"
FONT_PATHS = [
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
    ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
    ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", 0),
]


def register_font() -> None:
    last_error = None
    for path, idx in FONT_PATHS:
        if not os.path.exists(path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(FONT, path, subfontIndex=idx))
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"No CJK font registered: {last_error}")


def kind_of(n: int) -> str:
    if n == 1:
        return "intro"
    return "reading" if n % 2 == 0 else "writing"


def paint_paper(c: canvas.Canvas) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(HexColor("#F3EBE4"))
    c.rect(0, PAGE_H - 8, PAGE_W, 8, fill=1, stroke=0)


def round_rect(c, x, y, w, h, r, fill=None, stroke=None, sw=0.7):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
        c.roundRect(x, y, w, h, r, fill=1 if fill is not None else 0, stroke=1)
    else:
        c.setStrokeColor(fill or PAPER)
        c.setLineWidth(0.1)
        c.roundRect(x, y, w, h, r, fill=1 if fill is not None else 0, stroke=0)
    c.restoreState()


def text(c, s, x, y, size=10, color=INK, align="left", font=FONT):
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, s)
    elif align == "right":
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)


def dotted_blank(c, x, y, w, color=INK_FAINT):
    c.saveState()
    c.setStrokeColor(color)
    c.setDash(1.2, 1.6)
    c.setLineWidth(0.7)
    c.line(x, y, x + w, y)
    c.restoreState()


def hline(c, x, y, w, color=LINE, sw=0.6):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(sw)
    c.line(x, y, x + w, y)
    c.restoreState()


def checkbox(c, x, y, s=9):
    c.saveState()
    c.setStrokeColor(INK_FAINT)
    c.setLineWidth(0.8)
    c.roundRect(x, y, s, s, 1.5, fill=0, stroke=1)
    c.restoreState()


def chip(c, label, x, y, fill, ink, pad_x=8, h=16, size=8):
    tw = c.stringWidth(label, FONT, size)
    w = tw + pad_x * 2
    round_rect(c, x, y, w, h, h / 2, fill=fill, stroke=None)
    text(c, label, x + w / 2, y + 4.2, size=size, color=ink, align="center")
    return w


def link_to(c, dest, x, y, w, h):
    c.linkRect("", dest, (x, y, x + w, y + h), relative=0, thickness=0)


def bookmark(c, name, title, level=0):
    c.bookmarkPage(name, fit="Fit")
    c.addOutlineEntry(title, name, level=level, closed=0)


def footer(c, page_label, dest_toc="toc", dest_prev=None, dest_next=None):
    y = 16
    text(c, page_label, PAGE_W / 2, y, size=8, color=INK_FAINT, align="center")
    text(c, "目录", M, y, size=8, color=ACCENT)
    link_to(c, dest_toc, M - 4, y - 4, 28, 16)
    right = PAGE_W - M
    if dest_next:
        text(c, "下一页", right, y, size=8, color=ACCENT, align="right")
        link_to(c, dest_next, right - 36, y - 4, 36, 16)
        right -= 48
    if dest_prev:
        text(c, "上一页", right, y, size=8, color=ACCENT, align="right")
        link_to(c, dest_prev, right - 36, y - 4, 36, 16)
    hline(c, M, 28, CONTENT_W, HEADER_RULE, 0.5)


def section_title(c, x, y, w, number, title, hint=""):
    """Draw a numbered section head. Returns y under the head."""
    round_rect(c, x, y - 4, 18, 18, 9, fill=ACCENT)
    text(c, str(number), x + 9, y + 0.5, size=9, color=white, align="center")
    text(c, title, x + 24, y, size=12, color=INK)
    if hint:
        text(c, hint, x + w, y, size=8, color=INK_FAINT, align="right")
    hline(c, x, y - 8, w, HEADER_RULE, 0.6)
    return y - 18


def lined_block(c, x, y_top, w, n, gap=21):
    for i in range(n):
        yy = y_top - (i + 1) * gap
        hline(c, x, yy, w, LINE, 0.55)
    return n * gap


def field_row(c, items, x, y, total_w):
    """items: list of (label, blank_ratio)."""
    weights = [it[1] for it in items]
    s = sum(weights) or 1
    cursor = x
    for label, weight in items:
        slot = total_w * (weight / s)
        text(c, label, cursor, y, size=8.5, color=INK_SOFT)
        lw = c.stringWidth(label, FONT, 8.5) + 6
        dotted_blank(c, cursor + lw, y - 1, max(24, slot - lw - 10))
        cursor += slot


class Notebook:
    def __init__(self, path: str, lessons: int = 40):
        self.path = path
        self.lessons = lessons
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("高三英语课堂进度 · GoodNotes 模板")
        self.c.setAuthor("Gaokao English")
        self.c.setSubject("每节课：单词默写 + 语法；第2课起阅读/写作交替")
        self.page = 0
        self.word_pages = 3

    def new_page(self):
        if self.page:
            self.c.showPage()
        self.page += 1
        paint_paper(self.c)
        self.c.setPageCompression(1)

    def dest_lesson(self, n: int, part: int = 1) -> str:
        return f"L{n:02d}P{part}"

    def draw_cover(self):
        self.new_page()
        bookmark(self.c, "cover", "封面", 0)
        # outer frame
        round_rect(self.c, 36, 46, PAGE_W - 72, PAGE_H - 92, 18, fill=CARD, stroke=ROSE, sw=1.1)
        round_rect(self.c, 46, 56, PAGE_W - 92, PAGE_H - 112, 14, fill=None, stroke=ACCENT_SOFT, sw=0.8)

        text(self.c, "G A O K A O   E N G L I S H", PAGE_W / 2, PAGE_H - 130, 9, INK_FAINT, "center")
        text(self.c, "高三英语", PAGE_W / 2, PAGE_H - 188, 18, ROSE_INK, "center")
        text(self.c, "课堂进度手账", PAGE_W / 2, PAGE_H - 236, 32, INK, "center")
        hline(self.c, PAGE_W / 2 - 48, PAGE_H - 258, 96, ACCENT, 1.2)
        text(self.c, "单词默写  ·  语法  ·  阅读 / 写作交替", PAGE_W / 2, PAGE_H - 284, 11, INK_SOFT, "center")

        # type legend
        legend_y = PAGE_H - 340
        items = [
            ("第 1 课  导学", ACCENT_SOFT, ROSE_INK),
            ("第 2 / 4 / 6 课  阅读", SAGE_SOFT, SAGE_INK),
            ("第 3 / 5 / 7 课  写作", BLUE_SOFT, BLUE_INK),
        ]
        box_w = 148
        start_x = (PAGE_W - (box_w * 3 + 16 * 2)) / 2
        for i, (lab, bg, ink) in enumerate(items):
            x = start_x + i * (box_w + 16)
            round_rect(self.c, x, legend_y, box_w, 36, 10, fill=bg)
            text(self.c, lab, x + box_w / 2, legend_y + 13, 9, ink, "center")

        # info card
        info_y = 210
        round_rect(self.c, 90, info_y, PAGE_W - 180, 196, 12, fill=PAPER, stroke=LINE, sw=0.8)
        fields = ["学生姓名", "年级班级", "学期 / 学年", "任课教师"]
        for i, lab in enumerate(fields):
            y = info_y + 168 - i * 40
            text(self.c, lab, 114, y, 10, INK_SOFT)
            dotted_blank(self.c, 190, y - 1, PAGE_W - 190 - 114, INK_FAINT)

        text(self.c, "导入 GoodNotes → 打开为新笔记本，用 Apple Pencil 直接填写", PAGE_W / 2, 118, 9, INK_SOFT, "center")
        text(self.c, f"共 {self.lessons} 课  ·  每课 2 页  ·  含错词总表", PAGE_W / 2, 96, 8.5, INK_FAINT, "center")
        text(self.c, "点击目录中的课次即可跳转", PAGE_W / 2, 76, 8.5, ACCENT, "center")

    def draw_guide(self):
        self.new_page()
        bookmark(self.c, "guide", "使用说明", 0)
        text(self.c, "使用说明", M, PAGE_H - 58, 18, INK)
        text(self.c, "高三英语课堂进度  ·  GoodNotes 模板", M, PAGE_H - 80, 9, INK_SOFT)
        hline(self.c, M, PAGE_H - 92, CONTENT_W, ACCENT, 1.0)

        blocks = [
            (
                "课堂怎么排",
                [
                    "每节课固定两块：单词默写、语法。",
                    "剩下的一块按课次交替：第 2 课阅读，第 3 课写作，之后 4 读 5 写……",
                    "第 1 课是导学，第三块用来写学情、弱项和本学期目标。",
                ],
            ),
            (
                "这一页怎么填",
                [
                    "单词默写：先填范围和得分，再把错词填进表格（正确拼写 / 错误写法 / 词义）。",
                    "「再练」小格勾上表示已经订正并会写。易错规律可写发音、词形变化等。",
                    "语法、阅读、写作都是横线留白，按当堂内容直接写，不预设细项。",
                ],
            ),
            (
                "导入 GoodNotes",
                [
                    "隔空投送或「文件」打开本 PDF → 用 GoodNotes 打开 → 选择「导入为新笔记本」。",
                    "多页手账不要「设为纸张模板」；需要加课就复制对应阅读页或写作页，文末也有加课页。",
                    "页脚「目录 / 上一页 / 下一页」和目录课次都可以点。",
                ],
            ),
        ]
        y = PAGE_H - 120
        for title, lines in blocks:
            round_rect(self.c, M, y - 108, CONTENT_W, 124, 12, fill=CARD, stroke=LINE, sw=0.6)
            round_rect(self.c, M, y - 108, 6, 124, 3, fill=ACCENT)
            text(self.c, title, M + 22, y - 8, 13, INK)
            yy = y - 32
            for line in lines:
                text(self.c, "·  " + line, M + 22, yy, 9.5, INK_SOFT)
                yy -= 22
            y -= 148

        round_rect(self.c, M, 48, CONTENT_W, 70, 12, fill=ACCENT_SOFT)
        text(self.c, "填写小建议", M + 18, 96, 11, ROSE_INK)
        text(self.c, "默写错词尽量当天进表；反复错的再抄到文末「错词总表」。语法只记当堂那一条，阅读写错因比抄原文更有用。", M + 18, 72, 9, INK_SOFT)
        footer(self.c, "使用说明", dest_toc="toc", dest_next="toc")

    def draw_toc(self):
        self.new_page()
        bookmark(self.c, "toc", "目录", 0)
        text(self.c, "目录", M, PAGE_H - 58, 18, INK)
        text(self.c, "点课次进入该课第 1 页（单词 + 语法）", M, PAGE_H - 80, 9, INK_SOFT)
        hline(self.c, M, PAGE_H - 92, CONTENT_W, ACCENT, 1.0)

        # quick links
        y = PAGE_H - 122
        quick = [
            ("封面", "cover", ACCENT_SOFT, ROSE_INK),
            ("使用说明", "guide", ACCENT_SOFT, ROSE_INK),
            ("学期总览", "overview", SAGE_SOFT, SAGE_INK),
            ("错词总表", "words", BLUE_SOFT, BLUE_INK),
            ("加课页", "extra", ACCENT_SOFT, ROSE_INK),
        ]
        x = M
        for lab, dest, bg, ink in quick:
            w = chip(self.c, lab, x, y, bg, ink, pad_x=10, h=20, size=9)
            link_to(self.c, dest, x, y, w, 20)
            x += w + 10

        # lesson grid 5 columns
        cols = 5
        rows = (self.lessons + cols - 1) // cols
        grid_top = PAGE_H - 168
        cell_w = (CONTENT_W - 12 * (cols - 1)) / cols
        cell_h = 36
        gap_x, gap_y = 12, 10
        for n in range(1, self.lessons + 1):
            i = n - 1
            r, col = divmod(i, cols)
            # wait, I want row-major: col = i % cols, r = i // cols
            col = i % cols
            r = i // cols
            x = M + col * (cell_w + gap_x)
            y = grid_top - r * (cell_h + gap_y) - cell_h
            k = KIND[kind_of(n)]
            round_rect(self.c, x, y, cell_w, cell_h, 8, fill=k["chip"], stroke=None)
            text(self.c, f"第 {n:02d} 课", x + 10, y + 18, 10, INK)
            text(self.c, k["label"], x + 10, y + 6, 8, k["ink"])
            link_to(self.c, self.dest_lesson(n, 1), x, y, cell_w, cell_h)

        used_h = rows * (cell_h + gap_y)
        footer(self.c, "目录", dest_toc="toc", dest_prev="guide", dest_next="overview")
        _ = used_h

    def draw_overview(self):
        per_page = 20
        pages = (self.lessons + per_page - 1) // per_page
        col_w = [44, 90, 70, 200, 70, 61]
        headers = ["课次", "日期", "课型", "语法点（填写）", "默写得分", "完成"]
        for p in range(pages):
            self.new_page()
            if p == 0:
                bookmark(self.c, "overview", "学期总览", 0)
            text(self.c, "学期总览", M, PAGE_H - 58, 18, INK)
            text(self.c, "上课前在这里填日期；点课次进入当课。" + (f"  ·  {p + 1}/{pages}" if pages > 1 else ""), M, PAGE_H - 80, 9, INK_SOFT)
            hline(self.c, M, PAGE_H - 92, CONTENT_W, ACCENT, 1.0)

            y = PAGE_H - 118
            x = M
            round_rect(self.c, M, y - 4, CONTENT_W, 22, 4, fill=ACCENT_SOFT)
            for i, h in enumerate(headers):
                text(self.c, h, x + 6, y + 2, 8, ROSE_INK)
                x += col_w[i]
            y -= 8
            start = p * per_page + 1
            end = min(self.lessons, (p + 1) * per_page)
            row_h = 28
            for n in range(start, end + 1):
                y -= row_h
                k = KIND[kind_of(n)]
                bg = CARD if n % 2 else HexColor("#F7F1EC")
                round_rect(self.c, M, y - 6, CONTENT_W, row_h - 2, 4, fill=bg)
                round_rect(self.c, M + 8, y + 2, 4, 12, 2, fill=k["bar"])
                x = M
                vals = [f"{n:02d}", "", k["label"], "", "", ""]
                for i, v in enumerate(vals):
                    if i == 0:
                        text(self.c, v, x + 22, y + 2, 10, INK)
                        link_to(self.c, self.dest_lesson(n, 1), M, y - 6, 50, row_h - 2)
                    elif i == 2:
                        text(self.c, v, x + 8, y + 2, 9, k["ink"])
                    elif i == 5:
                        checkbox(self.c, x + 22, y + 1, 11)
                    else:
                        dotted_blank(self.c, x + 8, y + 1, col_w[i] - 16)
                    x += col_w[i]
            nxt = "overview2" if p == 0 and pages > 1 else (self.dest_lesson(1, 1) if p == pages - 1 else None)
            if p == 1:
                bookmark(self.c, "overview2", "学期总览 2", 1)
            footer(
                self.c,
                f"学期总览 {p + 1}/{pages}",
                dest_toc="toc",
                dest_prev="toc" if p == 0 else "overview",
                dest_next=nxt,
            )

    def draw_lesson_header(self, n: int, part: int, subtitle: str):
        k = KIND[kind_of(n)]
        # accent bar
        self.c.setFillColor(k["bar"])
        self.c.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)

        text(self.c, f"第 {n:02d} 课", M, PAGE_H - 42, 18, INK)
        chip_w = chip(self.c, k["label"], M + 86, PAGE_H - 46, k["chip"], k["ink"], pad_x=10, h=18, size=9)
        text(self.c, subtitle, M + 86 + chip_w + 12, PAGE_H - 41, 9, INK_SOFT)
        text(self.c, "高三英语课堂进度", PAGE_W - M, PAGE_H - 40, 8, INK_FAINT, "right")

        y = PAGE_H - 68
        if part == 1:
            field_row(
                self.c,
                [("日期", 1.3), ("星期", 0.7), ("姓名", 1.1), ("班级", 0.9)],
                M,
                y,
                CONTENT_W,
            )
        else:
            field_row(
                self.c,
                [("日期", 1.0), ("用时", 0.7), ("当堂完成", 0.8), ("订正", 0.7)],
                M,
                y,
                CONTENT_W,
            )
        hline(self.c, M, y - 12, CONTENT_W, HEADER_RULE, 0.7)
        return y - 24

    def draw_vocab_table(self, x, y_top, w, rows=12, start=1, show_lesson=False):
        if show_lesson:
            headers = [("序号", 36), ("课次", 50), ("正确拼写", 120), ("错误写法", 120), ("中文词义", 148), ("再练", 0)]
        else:
            headers = [("序号", 32), ("正确拼写", 132), ("错误写法", 132), ("中文词义", 178), ("再练", 0)]
        headers[-1] = ("再练", w - sum(h[1] for h in headers[:-1]))
        header_h, row_h = 22, 24
        table_h = header_h + rows * row_h
        y0 = y_top - table_h

        self.c.saveState()
        path = self.c.beginPath()
        path.roundRect(x, y0, w, table_h, 6)
        self.c.clipPath(path, stroke=0)
        self.c.setFillColor(CARD)
        self.c.rect(x, y0, w, table_h, fill=1, stroke=0)
        self.c.setFillColor(ACCENT_SOFT)
        self.c.rect(x, y_top - header_h, w, header_h, fill=1, stroke=0)

        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.45)
        yy = y_top - header_h
        for _ in range(rows + 1):
            self.c.line(x, yy, x + w, yy)
            yy -= row_h
        cx = x
        for _, cw in headers:
            self.c.line(cx, y_top, cx, y0)
            cx += cw
        self.c.line(x + w, y_top, x + w, y0)
        self.c.restoreState()

        cx = x
        for name, cw in headers:
            text(self.c, name, cx + cw / 2, y_top - 15, 8, ROSE_INK, "center")
            cx += cw
        for i in range(rows):
            yy = y_top - header_h - (i + 1) * row_h
            text(self.c, str(start + i), x + headers[0][1] / 2, yy + 8, 8, INK_FAINT, "center")
            checkbox(self.c, x + w - headers[-1][1] / 2 - 5, yy + 7, 10)
        round_rect(self.c, x, y0, w, table_h, 6, fill=None, stroke=LINE, sw=0.7)
        return table_h

    def draw_lesson_p1(self, n: int):
        self.new_page()
        dest = self.dest_lesson(n, 1)
        k = KIND[kind_of(n)]
        bookmark(self.c, dest, f"第 {n:02d} 课 · {k['label']}", 1)
        y = self.draw_lesson_header(n, 1, "第 1 页 · 单词默写 + 语法")

        # vocab card
        y = section_title(self.c, M, y, CONTENT_W, 1, "单词默写", "把本课默写错词填进表里")
        field_row(
            self.c,
            [("范围", 1.6), ("应默", 0.7), ("对", 0.55), ("错", 0.55), ("得分", 0.8)],
            M,
            y,
            CONTENT_W,
        )
        y -= 16
        table_h = self.draw_vocab_table(M, y, CONTENT_W, rows=12)
        y -= table_h + 16
        text(self.c, "易错规律", M, y, 8.5, INK_SOFT)
        dotted_blank(self.c, M + 52, y - 1, CONTENT_W - 52)
        y -= 18
        dotted_blank(self.c, M, y - 1, CONTENT_W)

        y -= 28
        y = section_title(self.c, M, y, CONTENT_W, 2, "语法", "留空填写：规则 / 例句 / 易错点")
        field_row(self.c, [("今日语法点", 1.0)], M, y, CONTENT_W)
        y -= 8
        n_lines = int((y - 46) // 21)
        lined_block(self.c, M, y, CONTENT_W, max(6, n_lines), 21)

        prev_dest = self.dest_lesson(n - 1, 2) if n > 1 else "overview"
        next_dest = self.dest_lesson(n, 2)
        footer(self.c, f"第 {n:02d} 课 · 1/2", dest_toc="toc", dest_prev=prev_dest, dest_next=next_dest)

    def draw_lesson_p2(self, n: int):
        self.new_page()
        dest = self.dest_lesson(n, 2)
        k = KIND[kind_of(n)]
        bookmark(self.c, dest, f"第 {n:02d} 课 · {k['third_title']}", 2)
        y = self.draw_lesson_header(n, 2, f"第 2 页 · {k['third_title']}")

        y = section_title(self.c, M, y, CONTENT_W, 3, k["third_title"], k["third_hint"])
        if kind_of(n) == "reading":
            field_row(self.c, [("材料 / 来源", 1.8), ("题量", 0.6), ("正确", 0.8)], M, y, CONTENT_W)
        elif kind_of(n) == "writing":
            field_row(self.c, [("题目 / 体裁", 2.0), ("词数", 0.7)], M, y, CONTENT_W)
        else:
            field_row(self.c, [("起点水平", 1.2), ("目标分数", 1.0)], M, y, CONTENT_W)
        y -= 8
        n_lines = int((y - 70) // 22)
        lined_block(self.c, M, y, CONTENT_W, max(10, n_lines), 22)

        # homework strip
        round_rect(self.c, M, 40, CONTENT_W, 36, 8, fill=CARD, stroke=LINE, sw=0.5)
        text(self.c, "课后作业 / 下节预习", M + 12, 58, 8.5, INK_SOFT)
        dotted_blank(self.c, M + 118, 57, CONTENT_W - 140)

        prev_dest = self.dest_lesson(n, 1)
        if n < self.lessons:
            next_dest = self.dest_lesson(n + 1, 1)
        else:
            next_dest = "words"
        footer(self.c, f"第 {n:02d} 课 · 2/2 · {k['label']}", dest_toc="toc", dest_prev=prev_dest, dest_next=next_dest)

    def draw_word_log(self):
        rows = 26
        for p in range(self.word_pages):
            self.new_page()
            dest = "words" if p == 0 else f"words{p + 1}"
            bookmark(self.c, dest, "错词总表" if p == 0 else f"错词总表 {p + 1}", 0 if p == 0 else 1)
            text(self.c, "错词总表", M, PAGE_H - 58, 18, INK)
            text(self.c, "把反复错的词从各课表格抄到这里，考前集中再默。" + f"  ·  {p + 1}/{self.word_pages}", M, PAGE_H - 80, 9, INK_SOFT)
            hline(self.c, M, PAGE_H - 92, CONTENT_W, ACCENT, 1.0)
            y = PAGE_H - 110
            self.draw_vocab_table(M, y, CONTENT_W, rows=rows, start=p * rows + 1, show_lesson=True)
            if p == 0:
                prev = self.dest_lesson(self.lessons, 2)
            else:
                prev = "words" if p == 1 else f"words{p}"
            nxt = "extra" if p == self.word_pages - 1 else f"words{p + 2}"
            footer(
                self.c,
                f"错词总表 {p + 1}/{self.word_pages}",
                dest_toc="toc",
                dest_prev=prev,
                dest_next=nxt,
            )

    def draw_extra_pages(self):
        extras = [
            ("reading", "加课页 · 阅读", "复制本页可继续上阅读课"),
            ("writing", "加课页 · 写作", "复制本页可继续上写作课"),
        ]
        for i, (kind, title, hint) in enumerate(extras):
            self.new_page()
            if i == 0:
                bookmark(self.c, "extra", "加课页", 0)
            else:
                bookmark(self.c, "extra2", "加课页 · 写作", 1)
            k = KIND[kind]
            self.c.setFillColor(k["bar"])
            self.c.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)
            text(self.c, title, M, PAGE_H - 42, 18, INK)
            chip(self.c, k["label"], M + 150, PAGE_H - 46, k["chip"], k["ink"], pad_x=10, h=18, size=9)
            text(self.c, hint, PAGE_W - M, PAGE_H - 40, 8, INK_FAINT, "right")
            y = PAGE_H - 68
            field_row(self.c, [("课次", 0.7), ("日期", 1.1), ("姓名", 1.0), ("班级", 0.9)], M, y, CONTENT_W)
            hline(self.c, M, y - 12, CONTENT_W, HEADER_RULE, 0.7)
            y = y - 28
            y = section_title(self.c, M, y, CONTENT_W, 1, "单词默写", "")
            field_row(self.c, [("范围", 1.6), ("应默", 0.7), ("对", 0.55), ("错", 0.55), ("得分", 0.8)], M, y, CONTENT_W)
            y -= 16
            table_h = self.draw_vocab_table(M, y, CONTENT_W, rows=8)
            y -= table_h + 22
            y = section_title(self.c, M, y, CONTENT_W, 2, "语法", "留空填写")
            field_row(self.c, [("今日语法点", 1.0)], M, y, CONTENT_W)
            y -= 8
            used = lined_block(self.c, M, y, CONTENT_W, 4, 20)
            y -= used + 18
            y = section_title(self.c, M, y, CONTENT_W, 3, k["third_title"], "留空填写")
            n_lines = int((y - 46) // 20)
            lined_block(self.c, M, y, CONTENT_W, max(5, n_lines), 20)
            last_words = "words" if self.word_pages == 1 else f"words{self.word_pages}"
            footer(
                self.c,
                title,
                dest_toc="toc",
                dest_prev=last_words if i == 0 else "extra",
                dest_next="extra2" if i == 0 else None,
            )

    def build(self):
        self.draw_cover()
        self.draw_guide()
        self.draw_toc()
        self.draw_overview()
        for n in range(1, self.lessons + 1):
            self.draw_lesson_p1(n)
            self.draw_lesson_p2(n)
        self.draw_word_log()
        self.draw_extra_pages()
        self.c.save()
        return self.page


def main():
    parser = argparse.ArgumentParser(description="Generate GoodNotes 高三英语课堂进度 template")
    parser.add_argument("--lessons", type=int, default=40)
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "gaokao-class-progress-goodnotes.pdf"),
    )
    args = parser.parse_args()
    register_font()
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
    nb = Notebook(args.output, lessons=args.lessons)
    pages = nb.build()
    print(f"Wrote {args.output} ({pages} pages, {args.lessons} lessons)")


if __name__ == "__main__":
    main()
