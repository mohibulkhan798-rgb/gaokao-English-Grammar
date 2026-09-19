#!/usr/bin/env python3
"""Generate GoodNotes-ready A4 landscape PDFs for 高三英语课堂进度."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "class-log.html"
PDF_PATH = ROOT / "高三英语课堂进度手账.pdf"
TEMPLATES = ROOT / "templates"

NUM_LESSONS = 20


def lesson_kind(n: int) -> str:
    if n == 1:
        return "opening"
    return "reading" if n % 2 == 0 else "writing"


KIND_META = {
    "opening": {
        "label": "开课建档",
        "short": "开课",
        "tone": "opening",
        "skill_title": "学情与学期安排",
        "hint": "第 1 节课先建档：记学情、目标和本学期语法主线。从第 2 节开始阅读、第 3 节开始写作，之后交替。",
    },
    "reading": {
        "label": "阅读课",
        "short": "阅读",
        "tone": "reading",
        "skill_title": "阅读",
        "hint": "本课在单词默写和语法之后做阅读。下一节课为写作。",
    },
    "writing": {
        "label": "写作课",
        "short": "写作",
        "tone": "writing",
        "skill_title": "写作",
        "hint": "本课在单词默写和语法之后做写作。下一节课为阅读。",
    },
}


CSS = r"""
:root {
  --paper: #FAF6F1;
  --card: #FFFCFA;
  --ink: #4A433E;
  --ink-soft: #8A8178;
  --ink-faint: #B4AAA2;
  --line: rgba(160, 128, 118, 0.28);
  --line-soft: rgba(160, 128, 118, 0.16);
  --accent: #C9A39C;
  --accent-soft: #F4E8E4;
  --rose: #D9A39A;
  --sage: #8FA392;
  --sage-soft: #E6EEE7;
  --opening: #C4B39A;
  --opening-soft: #F3EEE4;
  --rule: 7.6mm;
  --font-serif: "Noto Serif CJK SC", "Noto Serif SC", "Source Han Serif SC", serif;
  --font-sans: "Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", sans-serif;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: #d8cfc6;
  color: var(--ink);
  font-family: var(--font-sans);
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
@page {
  size: A4 landscape;
  margin: 0;
}
.page {
  width: 297mm;
  height: 210mm;
  background: var(--paper);
  padding: 8.2mm 10mm 6.5mm;
  position: relative;
  overflow: hidden;
  page-break-after: always;
  break-after: page;
  display: flex;
  flex-direction: column;
}
.page:last-child {
  page-break-after: auto;
  break-after: auto;
}
.page::before {
  content: "";
  position: absolute;
  inset: 4.2mm;
  border: 0.35mm solid rgba(180, 150, 140, 0.28);
  border-radius: 2.2mm;
  pointer-events: none;
}
.page.reading { --tone: var(--sage); --tone-soft: var(--sage-soft); --tone-ink: #4F6A55; }
.page.writing { --tone: var(--rose); --tone-soft: var(--accent-soft); --tone-ink: #8C5852; }
.page.opening { --tone: var(--opening); --tone-soft: var(--opening-soft); --tone-ink: #7A6A4E; }
.page.plain { --tone: var(--accent); --tone-soft: var(--accent-soft); --tone-ink: #8F6863; }

.kicker {
  font-size: 9.5pt;
  letter-spacing: 0.22em;
  color: var(--ink-soft);
  font-weight: 500;
}
h1, h2, h3 { font-family: var(--font-serif); font-weight: 600; margin: 0; color: #5C534C; }
a { color: inherit; text-decoration: none; }

/* ----- Cover ----- */
.cover {
  align-items: stretch;
  justify-content: space-between;
  background:
    radial-gradient(ellipse 70% 55% at 8% -10%, rgba(232, 196, 188, 0.42), transparent 55%),
    radial-gradient(ellipse 55% 50% at 100% 0%, rgba(214, 226, 216, 0.38), transparent 50%),
    var(--paper);
}
.cover-top { display: flex; justify-content: space-between; align-items: flex-start; }
.cover-mark {
  width: 14mm; height: 14mm; border-radius: 4mm;
  background: var(--accent-soft); color: #8F6863;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-serif); font-size: 16pt;
}
.cover-hero { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 4mm 6mm 2mm; }
.cover-hero h1 {
  font-size: 34pt;
  letter-spacing: 0.12em;
  line-height: 1.2;
  margin: 3mm 0 4mm;
}
.cover-hero .lead {
  font-size: 12.5pt;
  color: var(--ink-soft);
  max-width: 180mm;
  line-height: 1.7;
}
.rhythm {
  display: flex; gap: 3.2mm; margin-top: 8mm; flex-wrap: wrap;
}
.chip {
  min-width: 28mm;
  padding: 2.4mm 3.5mm 2.2mm;
  border-radius: 2.2mm;
  background: var(--card);
  border: 0.3mm solid rgba(180, 150, 140, 0.22);
}
.chip b { display: block; font-size: 8.5pt; color: var(--ink-soft); font-weight: 500; letter-spacing: 0.08em; }
.chip span { display: block; font-family: var(--font-serif); font-size: 13pt; margin-top: 0.8mm; }
.chip.reading { background: var(--sage-soft); }
.chip.writing { background: var(--accent-soft); }
.chip.opening { background: var(--opening-soft); }
.cover-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4mm 10mm;
  width: 170mm;
  margin-top: 9mm;
}
.field-line {
  display: flex; align-items: flex-end; gap: 2.5mm;
  border-bottom: 0.35mm solid var(--line);
  min-height: 9mm;
  padding-bottom: 1.2mm;
  font-size: 11pt;
  color: var(--ink-soft);
}
.field-line i { font-style: normal; white-space: nowrap; }
.field-line .blank { flex: 1; }
.cover-foot {
  display: flex; justify-content: space-between; align-items: flex-end;
  font-size: 9.5pt; color: var(--ink-soft);
}
.toc-links { display: flex; gap: 4mm; }
.toc-links a {
  padding: 1.8mm 4.2mm;
  border-radius: 999px;
  background: #fff;
  border: 0.3mm solid rgba(180, 150, 140, 0.28);
  font-size: 9.5pt;
}

/* ----- Shared lesson chrome ----- */
.header {
  display: flex; align-items: center; gap: 3.5mm;
  padding-bottom: 3.2mm;
  border-bottom: 0.45mm solid rgba(160, 128, 118, 0.28);
  flex: 0 0 auto;
}
.brand {
  font-family: var(--font-serif);
  font-size: 13.5pt;
  letter-spacing: 0.08em;
}
.lesson-no {
  font-family: var(--font-serif);
  font-size: 15pt;
  margin-left: 1mm;
}
.badge {
  margin-left: 1mm;
  font-size: 9.5pt;
  letter-spacing: 0.12em;
  padding: 1.1mm 3.4mm 0.9mm;
  border-radius: 999px;
  background: var(--tone-soft);
  color: var(--tone-ink);
  font-weight: 600;
}
.header-fields {
  margin-left: auto;
  display: flex; gap: 4.5mm;
  font-size: 10pt; color: var(--ink-soft);
}
.mini-field {
  display: flex; align-items: flex-end; gap: 1.6mm;
  min-width: 28mm;
  border-bottom: 0.3mm solid var(--line);
  padding-bottom: 0.6mm;
}
.mini-field.wide { min-width: 36mm; }
.body {
  flex: 1;
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  gap: 5.5mm;
  min-height: 0;
  padding-top: 3.4mm;
}
.col {
  display: flex; flex-direction: column; min-height: 0; min-width: 0;
}
.sec-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 3mm;
  margin-bottom: 2.2mm;
}
.sec-head h2 {
  font-size: 13pt;
  letter-spacing: 0.14em;
  display: flex; align-items: center; gap: 2mm;
}
.dot {
  width: 2.6mm; height: 2.6mm; border-radius: 50%;
  background: var(--tone);
  display: inline-block;
}
.sec-note { font-size: 8.5pt; color: var(--ink-soft); }
.meta-grid {
  display: grid;
  grid-template-columns: 1.4fr 0.7fr 0.7fr 0.7fr;
  gap: 2mm;
  margin-bottom: 2.4mm;
}
.box {
  background: #fff;
  border: 0.3mm solid var(--line-soft);
  border-radius: 1.6mm;
  padding: 1.4mm 2.2mm 1.2mm;
  min-height: 9.2mm;
  display: flex; flex-direction: column; justify-content: flex-end;
}
.box label {
  font-size: 7.8pt;
  color: var(--ink-soft);
  letter-spacing: 0.08em;
  margin-bottom: 0.6mm;
}
.box .line {
  border-bottom: 0.28mm solid var(--line);
  height: 5.4mm;
}
table.mistakes {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  font-size: 8.4pt;
  table-layout: fixed;
}
table.mistakes th {
  background: var(--tone-soft);
  color: var(--tone-ink);
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 1.4mm 1.2mm;
  border: 0.28mm solid rgba(160, 128, 118, 0.28);
  text-align: center;
  white-space: nowrap;
}
table.mistakes td {
  border: 0.28mm solid rgba(160, 128, 118, 0.22);
  height: 8.6mm;
  padding: 0 1.2mm;
  background-image: linear-gradient(to bottom, transparent 6.8mm, rgba(180,150,140,0.12) 6.8mm);
  background-repeat: no-repeat;
}
table.mistakes td.idx {
  text-align: center;
  color: var(--ink-faint);
  font-size: 8pt;
  background-image: none;
  width: 8mm;
}
table.mistakes td.chk {
  width: 9mm;
  background-image: none;
  text-align: center;
}
.chkbox {
  display: inline-block;
  width: 3.6mm; height: 3.6mm;
  border: 0.32mm solid rgba(140, 110, 100, 0.55);
  border-radius: 0.6mm;
  vertical-align: middle;
}
.legend {
  display: flex; gap: 3mm; align-items: center;
  font-size: 8pt; color: var(--ink-soft);
  margin-top: 1.4mm;
}
.sub-label {
  font-size: 9pt;
  color: var(--ink-soft);
  letter-spacing: 0.1em;
  margin: 2.2mm 0 1.2mm;
}
.ruled {
  flex: 1;
  min-height: 16mm;
  background-color: #fff;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent calc(var(--rule) - 0.28mm),
    rgba(160, 128, 118, 0.22) calc(var(--rule) - 0.28mm),
    rgba(160, 128, 118, 0.22) var(--rule)
  );
  border: 0.3mm solid var(--line-soft);
  border-radius: 1.6mm;
}
.right-stack { display: flex; flex-direction: column; min-height: 0; gap: 3.2mm; }
.panel {
  display: flex; flex-direction: column; min-height: 0;
  flex: 1;
}
.panel.grammar { flex: 1.18; }
.checks {
  display: flex; flex-wrap: wrap; gap: 2.2mm 3.5mm;
  font-size: 9.5pt;
  color: var(--ink-soft);
  margin-bottom: 1.8mm;
}
.checks span { display: inline-flex; align-items: center; gap: 1.4mm; }
.footer {
  flex: 0 0 auto;
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 2.2mm;
  font-size: 8.2pt;
  color: var(--ink-faint);
  letter-spacing: 0.06em;
}
.footer a { color: var(--ink-soft); }

/* ----- Guide / overview ----- */
.guide-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 6mm;
  padding-top: 4mm;
  min-height: 0;
}
.card {
  background: #fff;
  border: 0.3mm solid var(--line-soft);
  border-radius: 3mm;
  padding: 4.5mm 5mm;
  display: flex; flex-direction: column;
}
.card h2 { font-size: 14pt; letter-spacing: 0.1em; margin-bottom: 3mm; }
.card p, .card li { font-size: 10.5pt; line-height: 1.65; color: #5C534C; }
.card ol, .card ul { margin: 0; padding-left: 5mm; }
.card li { margin-bottom: 1.6mm; }
.flow {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 2.2mm;
  margin-top: 3mm;
}
.flow .chip { min-width: 0; text-align: center; }
.tiny { font-size: 9pt; color: var(--ink-soft); margin-top: 3mm; line-height: 1.55; }
table.overview {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  font-size: 8.3pt;
  table-layout: fixed;
}
table.overview th {
  background: var(--accent-soft);
  color: #8F6863;
  font-weight: 600;
  padding: 1.5mm 1.3mm;
  border: 0.28mm solid rgba(160, 128, 118, 0.25);
  text-align: center;
}
.overview-wrap {
  flex: 1;
  padding-top: 3mm;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
table.overview td {
  border: 0.28mm solid rgba(160, 128, 118, 0.2);
  height: 6.6mm;
  padding: 0 1.4mm;
}
table.overview td.c { text-align: center; color: var(--ink-soft); }
table.overview tr.reading td.kind { background: var(--sage-soft); color: #4F6A55; }
table.overview tr.writing td.kind { background: var(--accent-soft); color: #8C5852; }
table.overview tr.opening td.kind { background: var(--opening-soft); color: #7A6A4E; }

@media screen {
  body { padding: 8mm 0 14mm; }
  .page {
    margin: 0 auto 8mm;
    box-shadow: 0 8px 28px rgba(90, 70, 60, 0.16);
    border-radius: 1mm;
  }
}
@media print {
  body { background: none; padding: 0; }
  .page { box-shadow: none; margin: 0; border-radius: 0; }
}
"""


def ruled_note(label: str) -> str:
    return f'<div class="sub-label">{label}</div><div class="ruled"></div>'


def word_table(rows: int = 10) -> str:
    body = []
    for i in range(1, rows + 1):
        body.append(
            f"<tr><td class='idx'>{i}</td><td></td><td></td><td></td><td></td>"
            f"<td class='chk'><span class='chkbox'></span></td></tr>"
        )
    return f"""
    <table class="mistakes">
      <colgroup>
        <col style="width:12mm">
        <col>
        <col>
        <col>
        <col>
        <col style="width:11mm">
      </colgroup>
      <thead>
        <tr>
          <th>序号</th>
          <th>正确拼写</th>
          <th>错误写法</th>
          <th>中文词义</th>
          <th>订正 / 再默</th>
          <th>会了</th>
        </tr>
      </thead>
      <tbody>
        {''.join(body)}
      </tbody>
    </table>
    <div class="legend">
      <span>填写提示：只记错词即可，对的不用抄。</span>
      <span>「会了」在订正后再勾。</span>
    </div>
    """


def skill_block(kind: str) -> str:
    if kind == "opening":
        return f"""
        <div class="panel">
          <div class="sec-head"><h2><span class="dot"></span>学情与学期安排</h2></div>
          <div class="checks">
            <span><span class="chkbox"></span>词汇底子</span>
            <span><span class="chkbox"></span>语法底子</span>
            <span><span class="chkbox"></span>阅读速度</span>
            <span><span class="chkbox"></span>写作表达</span>
          </div>
          {ruled_note("目前问题 / 本学期目标 / 语法主线（留空填写）")}
        </div>
        """
    if kind == "reading":
        return f"""
        <div class="panel">
          <div class="sec-head">
            <h2><span class="dot"></span>阅读</h2>
            <div class="sec-note">本栏留空，记篇目、错题和长难句</div>
          </div>
          <div class="meta-grid" style="grid-template-columns:1.2fr .8fr .7fr .7fr">
            <div class="box"><label>材料 / 篇目</label><div class="line"></div></div>
            <div class="box"><label>体裁</label><div class="line"></div></div>
            <div class="box"><label>用时</label><div class="line"></div></div>
            <div class="box"><label>正确 __ / __</label><div class="line"></div></div>
          </div>
          {ruled_note("阅读留白：错题定位、选项分析、生词与长难句")}
        </div>
        """
    return f"""
        <div class="panel">
          <div class="sec-head">
            <h2><span class="dot"></span>写作</h2>
            <div class="sec-note">本栏留空，记题型、框架和好词好句</div>
          </div>
          <div class="checks">
            <span><span class="chkbox"></span>应用文</span>
            <span><span class="chkbox"></span>读后续写</span>
            <span><span class="chkbox"></span>概要写作</span>
            <span><span class="chkbox"></span>其他</span>
          </div>
          <div class="meta-grid" style="grid-template-columns:1.4fr .8fr .8fr">
            <div class="box"><label>题目 / 任务</label><div class="line"></div></div>
            <div class="box"><label>体裁要点</label><div class="line"></div></div>
            <div class="box"><label>用时</label><div class="line"></div></div>
          </div>
          {ruled_note("写作留白：审题、框架、好词好句、问题与升格")}
        </div>
        """


def lesson_page(n: int | None, kind: str, page_label: str, total_label: str, page_id: str) -> str:
    meta = KIND_META[kind]
    title = f"第 {n} 节课" if n else "空白加页"
    return f"""
<section class="page {kind}" id="{page_id}">
  <div class="header">
    <div class="brand">高三英语课堂进度</div>
    <div class="lesson-no">{title}</div>
    <div class="badge">{meta['label']}</div>
    <div class="header-fields">
      <div class="mini-field wide"><span>日期</span></div>
      <div class="mini-field"><span>班级</span></div>
      <div class="mini-field"><span>星期</span></div>
      <div class="mini-field"><span>学生</span></div>
    </div>
  </div>
  <div class="body">
    <div class="col">
      <div class="sec-head">
        <h2><span class="dot"></span>单词默写</h2>
        <div class="sec-note">错词汇总表，方便当堂填写</div>
      </div>
      <div class="meta-grid">
        <div class="box"><label>默写范围（单元 / 词表）</label><div class="line"></div></div>
        <div class="box"><label>应默</label><div class="line"></div></div>
        <div class="box"><label>对</label><div class="line"></div></div>
        <div class="box"><label>错</label><div class="line"></div></div>
      </div>
      {word_table(10)}
      {ruled_note("易错规律 / 下次重点")}
    </div>
    <div class="col right-stack">
      <div class="panel grammar">
        <div class="sec-head">
          <h2><span class="dot"></span>语法</h2>
          <div class="sec-note">本栏留空，填写今日语法</div>
        </div>
        <div class="meta-grid" style="grid-template-columns:1fr">
          <div class="box"><label>今日语法点</label><div class="line"></div></div>
        </div>
        {ruled_note("规则要点 · 例句 · 易错（留空填写）")}
      </div>
      {skill_block(kind)}
    </div>
  </div>
  <div class="footer">
    <div>{meta['hint']}</div>
    <div><a href="#overview">目录</a>　{page_label} / {total_label}</div>
  </div>
</section>
"""


def cover_page() -> str:
    chips = [
        ("opening", "第 1 节", "开课建档"),
        ("reading", "第 2 节", "阅读"),
        ("writing", "第 3 节", "写作"),
        ("reading", "第 4 节", "阅读"),
        ("writing", "第 5 节", "写作"),
        ("reading", "之后", "继续交替"),
    ]
    chip_html = "".join(
        f'<div class="chip {k}"><b>{a}</b><span>{b}</span></div>' for k, a, b in chips
    )
    return f"""
<section class="page cover plain" id="cover">
  <div class="cover-top">
    <div>
      <div class="kicker">GAOKAO ENGLISH · GOODNOTES</div>
    </div>
    <div class="cover-mark">英</div>
  </div>
  <div class="cover-hero">
    <div class="kicker">高考英语 · 课堂手账</div>
    <h1>高三课堂进度</h1>
    <p class="lead">每节课固定记录单词默写和语法；剩下的课时按阅读、写作交替。从第二节课开始阅读，第三节课开始写作。</p>
    <div class="rhythm">{chip_html}</div>
    <div class="cover-fields">
      <div class="field-line"><i>学生</i><span class="blank"></span></div>
      <div class="field-line"><i>班级</i><span class="blank"></span></div>
      <div class="field-line"><i>学期</i><span class="blank"></span></div>
      <div class="field-line"><i>教师</i><span class="blank"></span></div>
    </div>
  </div>
  <div class="cover-foot">
    <div>A4 横向 · 导入 GoodNotes 后用 Apple Pencil 直接填写</div>
    <div class="toc-links">
      <a href="#guide">使用说明</a>
      <a href="#overview">学期总览</a>
      <a href="#lesson-1">第 1 节课</a>
    </div>
  </div>
</section>
"""


def guide_page() -> str:
    flow = "".join(
        f'<div class="chip {lesson_kind(i)}"><b>第 {i} 节</b><span>{KIND_META[lesson_kind(i)]["short"]}</span></div>'
        for i in range(1, 9)
    )
    return f"""
<section class="page plain" id="guide">
  <div class="header">
    <div class="brand">使用说明</div>
    <div class="badge">怎么用这本手账</div>
  </div>
  <div class="guide-grid">
    <div class="card">
      <h2>课堂节奏</h2>
      <p>每一节课都先完成两件固定事项：<b>单词默写</b>和<b>语法</b>。剩余时间从第 2 节起按阅读 / 写作交替。</p>
      <div class="flow">{flow}</div>
      <p class="tiny">左侧错词表只填写默错的词：正确拼写、错误写法、词义、订正后再勾「会了」。语法栏和阅读栏都故意留白，方便手写。</p>
    </div>
    <div class="card">
      <h2>导入 GoodNotes</h2>
      <ol>
        <li>把「高三英语课堂进度手账.pdf」导入 GoodNotes，作为一本新笔记打开即可逐页填写。</li>
        <li>若要在模板库里重复加页：把 templates 文件夹中的「阅读课.pdf」或「写作课.pdf」导入「Notebook Templates」。多页 PDF 在模板库里只会保存第一页，所以单页模版要分开导入。</li>
        <li>纸张尺寸选 <b>A4 · Landscape</b>。不要选 GoodNotes Standard，否则比例会变形。</li>
        <li>学期总览页用来登记每一节的日期、语法点和对错，方便回头找课。</li>
      </ol>
      <p class="tiny">本手账预置 20 节编号课页，末尾另附阅读课、写作课空白加页，可在 GoodNotes 中复制后继续使用。</p>
    </div>
  </div>
  <div class="footer">
    <div>固定结构：单词默写 + 语法 +（阅读或写作）</div>
    <div><a href="#cover">封面</a>　2 / 25</div>
  </div>
</section>
"""


def overview_page() -> str:
    rows = []
    for n in range(1, 25):
        kind = lesson_kind(n)
        label = KIND_META[kind]["short"]
        cell = (
            f"<a href='#lesson-{n}'>{n:02d}</a>"
            if n <= NUM_LESSONS
            else f"{n:02d}"
        )
        rows.append(
            f"<tr class='{kind}'>"
            f"<td class='c'>{cell}</td>"
            f"<td></td><td class='c'></td>"
            f"<td class='c kind'>{label}</td>"
            f"<td></td><td class='c'></td><td></td><td></td>"
            f"</tr>"
        )
    return f"""
<section class="page plain" id="overview">
  <div class="header">
    <div class="brand">学期总览</div>
    <div class="badge">24 节课进度</div>
    <div class="header-fields">
      <div class="mini-field wide"><span>学期</span></div>
      <div class="mini-field wide"><span>班级</span></div>
    </div>
  </div>
  <div class="overview-wrap">
    <table class="overview">
      <colgroup>
        <col style="width:12mm">
        <col style="width:28mm">
        <col style="width:14mm">
        <col style="width:16mm">
        <col>
        <col style="width:16mm">
        <col>
        <col style="width:28mm">
      </colgroup>
      <thead>
        <tr>
          <th>课次</th>
          <th>日期</th>
          <th>星期</th>
          <th>课型</th>
          <th>今日语法点</th>
          <th>错词数</th>
          <th>阅读 / 写作要点</th>
          <th>备注</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
  <div class="footer">
    <div>课型已按「第 2 节阅读、第 3 节写作、之后交替」预填。第 21 节起复制末尾空白页继续记。</div>
    <div><a href="#lesson-1">进入第 1 节</a>　3 / 25</div>
  </div>
</section>
"""


def build_html() -> str:
    total = 3 + NUM_LESSONS + 2  # cover, guide, overview, lessons, 2 blanks
    pages = [cover_page(), guide_page(), overview_page()]
    for n in range(1, NUM_LESSONS + 1):
        pages.append(
            lesson_page(
                n,
                lesson_kind(n),
                str(n + 3),
                str(total),
                f"lesson-{n}",
            )
        )
    pages.append(
        lesson_page(None, "reading", str(total - 1), str(total), "blank-reading")
    )
    pages.append(
        lesson_page(None, "writing", str(total), str(total), "blank-writing")
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>高三英语课堂进度 · GoodNotes 模版</title>
<style>{CSS}</style>
</head>
<body>
{''.join(pages)}
</body>
</html>
"""


def single_lesson_html(kind: str, n: int | None, title: str) -> str:
    page = lesson_page(n, kind, "1", "1", "top")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{page}
</body>
</html>
"""


def chrome_pdf(html: Path, pdf: Path) -> None:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "google-chrome-stable",
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        "--font-render-hinting=none",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={pdf}",
        html.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"wrote {pdf} ({pdf.stat().st_size} bytes)")


def main() -> None:
    html = build_html()
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"wrote {HTML_PATH}")
    chrome_pdf(HTML_PATH, PDF_PATH)

    extras = [
        ("阅读课.pdf", "reading", None, "阅读课空白模版"),
        ("写作课.pdf", "writing", None, "写作课空白模版"),
        ("开课第1节.pdf", "opening", 1, "开课第1节模版"),
    ]
    for filename, kind, n, title in extras:
        path = ROOT / "_tmp.html"
        path.write_text(single_lesson_html(kind, n, title), encoding="utf-8")
        chrome_pdf(path, TEMPLATES / filename)
        path.unlink(missing_ok=True)

    overview_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>学期总览</title>
<style>{CSS}</style>
</head>
<body>
{overview_page()}
</body>
</html>
"""
    tmp = ROOT / "_tmp.html"
    tmp.write_text(overview_html, encoding="utf-8")
    chrome_pdf(tmp, TEMPLATES / "学期总览.pdf")
    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
