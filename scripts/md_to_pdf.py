#!/usr/bin/env python3
"""Render an eCommerce strategy Markdown file as a shareable report-class PDF."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path


FONT_STACK = (
    'system-ui, -apple-system, BlinkMacSystemFont, "Helvetica Neue", '
    '"PingFang SC", "Hiragino Sans GB", "Noto Sans CJK SC", '
    '"Microsoft YaHei", "Droid Sans Fallback", sans-serif'
)


CSS_TEMPLATE = r"""
@page {
    size: A4;
    margin: 27mm 22mm 23mm 22mm;
    background: #F8F8F6;

    @top-center {
        content: "HEADER_TEXT";
        font-family: FONT_STACK;
        font-size: 7.7pt;
        color: #77736E;
        border-bottom: 0.5pt solid #DEDAD3;
        padding-bottom: 3mm;
    }

    @bottom-center {
        content: "第 " counter(page) " 页";
        font-family: FONT_STACK;
        font-size: 7.7pt;
        color: #77736E;
        border-top: 0.8pt solid #C96442;
        padding-top: 2.2mm;
    }
}

@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

html,
body {
    background: #F8F8F6;
}

html {
    font-family: FONT_STACK;
    color: #171615;
}

body {
    margin: 0;
    font-family: FONT_STACK;
    font-size: 10.8pt;
    line-height: 1.86;
    text-align: justify;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}

.cover {
    min-height: 235mm;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
}

.cover-eyebrow {
    margin-bottom: 15mm;
    color: #9B4B36;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 2.5pt;
}

.cover .cover-title {
    max-width: 155mm;
    margin: 0;
    padding: 0;
    border: 0;
    color: #C45E40;
    font-size: 28pt;
    font-weight: 760;
    letter-spacing: 0.5pt;
    line-height: 1.34;
    page-break-before: avoid;
    page-break-after: avoid;
}

.cover-subtitle {
    margin-top: 8mm;
    color: #65615C;
    font-size: 13pt;
    line-height: 1.55;
}

.cover-divider {
    width: 43mm;
    margin: 13mm 0 10mm;
    border: 0;
    border-top: 1.5pt solid #C96442;
}

.cover-meta {
    width: 100%;
    border-top: 0.5pt solid #DEDAD3;
    padding-top: 5mm;
    color: #625E59;
    font-size: 9.2pt;
    line-height: 1.65;
}

.cover-meta-row {
    display: grid;
    grid-template-columns: 25mm auto;
    column-gap: 4mm;
    margin: 1.5mm 0;
}

.cover-meta-label {
    color: #98918A;
}

.cover-footer {
    margin-top: 10mm;
    color: #8B857F;
    font-size: 8.5pt;
    letter-spacing: 0.3pt;
}

.reading-guide {
    page-break-after: always;
    min-height: 215mm;
    padding-top: 7mm;
}

.reading-guide .guide-label {
    color: #9B4B36;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 2pt;
}

.reading-guide h1 {
    page-break-before: avoid;
    margin: 5mm 0 10mm;
}

.guide-note {
    max-width: 135mm;
    margin: 0 0 10mm;
    color: #6F6A64;
    font-size: 10pt;
    line-height: 1.75;
}

.toc {
    margin: 0;
    padding: 0;
    list-style: none;
    counter-reset: guide-item;
}

.toc li {
    counter-increment: guide-item;
    display: grid;
    grid-template-columns: 9mm auto;
    column-gap: 4mm;
    margin: 0;
    padding: 4mm 0;
    border-bottom: 0.5pt solid #DEDAD3;
    break-inside: avoid;
}

.toc li::before {
    content: counter(guide-item, decimal-leading-zero);
    color: #C96442;
    font-size: 8.5pt;
    font-weight: 700;
    padding-top: 0.7mm;
}

.toc a {
    color: #1F1D1B;
    font-size: 11.2pt;
    font-weight: 600;
    line-height: 1.55;
}

.report-body > h1:first-child {
    margin-top: 0;
}

h1,
h2,
h3,
h4 {
    text-align: left;
    break-after: avoid;
}

h1 {
    margin: 0 0 9mm;
    padding: 0 0 4mm;
    border-bottom: 2pt solid #C96442;
    color: #C45E40;
    font-size: 21pt;
    font-weight: 750;
    line-height: 1.38;
}

.report-body > h1 {
    page-break-before: always;
}

h2 {
    margin: 12mm 0 6mm;
    padding-left: 4mm;
    border-left: 4pt solid #C96442;
    color: #B65339;
    font-size: 15.5pt;
    font-weight: 720;
    line-height: 1.4;
}

h3 {
    margin: 8mm 0 4mm;
    padding-left: 3mm;
    border-left: 2pt solid #D89A84;
    color: #9D4936;
    font-size: 12.5pt;
    font-weight: 700;
    line-height: 1.45;
}

h4 {
    margin: 6mm 0 3mm;
    color: #4D4945;
    font-size: 11.3pt;
    font-weight: 700;
    line-height: 1.5;
}

p {
    margin: 2.8mm 0;
    color: #1D1B19;
    orphans: 3;
    widows: 3;
}

strong,
b {
    color: #171615;
    font-weight: 720;
}

blockquote {
    margin: 6mm 0;
    padding: 5.5mm 6mm;
    border: 0;
    border-left: 2.5pt solid #D58A70;
    background: #F0EEE6;
    color: #292623;
    font-size: 10.5pt;
    line-height: 1.82;
    break-inside: avoid;
}

blockquote p {
    margin: 1.5mm 0;
}

blockquote h1 {
    margin: 1mm 0 3mm;
    padding: 0 0 2.5mm;
    border-bottom: 0.8pt solid #D58A70;
    color: #B65339;
    font-size: 15pt;
    line-height: 1.45;
    page-break-before: avoid;
}

ul,
ol {
    margin: 3mm 0;
    padding-left: 8mm;
}

li {
    margin: 0 0 2mm;
    padding-left: 1mm;
    color: #1D1B19;
    line-height: 1.78;
}

li::marker {
    color: #B95B42;
}

hr {
    margin: 7mm 0;
    border: 0;
    border-top: 0.5pt solid #DEDAD3;
}

table {
    width: 100%;
    margin: 5mm 0 7mm;
    border-collapse: collapse;
    table-layout: auto;
    background: transparent;
    font-size: 9pt;
    text-align: left;
}

thead {
    display: table-header-group;
}

tr {
    break-inside: avoid;
}

thead th {
    padding: 3.2mm 3mm;
    border-top: 1.2pt solid #B75B43;
    border-bottom: 0.8pt solid #77736E;
    color: #4B4641;
    font-weight: 720;
    line-height: 1.45;
    vertical-align: bottom;
}

tbody td {
    padding: 3.2mm 3mm;
    border-bottom: 0.5pt solid #DDD8D0;
    color: #2C2926;
    line-height: 1.55;
    vertical-align: top;
    overflow-wrap: anywhere;
    word-break: break-word;
}

tbody tr:last-child td {
    border-bottom: 0.8pt solid #B8B1A8;
}

table.cols-5 {
    font-size: 8.1pt;
}

table.cols-6,
table.cols-7,
table.cols-8 {
    font-size: 7.4pt;
}

table.cols-5 th,
table.cols-5 td,
table.cols-6 th,
table.cols-6 td,
table.cols-7 th,
table.cols-7 td,
table.cols-8 th,
table.cols-8 td {
    padding: 2.5mm 2.1mm;
    line-height: 1.43;
}

code {
    padding: 0.5mm 1.2mm;
    border-radius: 2pt;
    background: #EDEAE3;
    color: #4A443E;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 9.3pt;
}

pre {
    margin: 5mm 0;
    padding: 5mm;
    border-radius: 3pt;
    background: #EDEAE3;
    color: #302D2A;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 8.8pt;
    line-height: 1.65;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

pre code {
    padding: 0;
    background: transparent;
}

a {
    color: #A94F38;
    text-decoration: none;
    overflow-wrap: anywhere;
}

.sources-appendix {
    color: #4F4B47;
    font-size: 9.2pt;
    page-break-before: always;
}

.sources-appendix h1 {
    margin-bottom: 7mm;
    padding-bottom: 3mm;
    border-bottom: 0.7pt solid #AAA39B;
    color: #4F4B47;
    font-size: 15.5pt;
    font-weight: 500;
    letter-spacing: 0;
}

.sources-appendix h2 {
    margin: 7mm 0 3mm;
    padding: 0;
    border: 0;
    color: #5D5853;
    font-size: 10.5pt;
    font-weight: 500;
    line-height: 1.55;
}

.sources-appendix ul {
    margin: 1.5mm 0 5mm;
    padding: 0;
    list-style: none;
}

.sources-appendix li {
    margin: 0 0 2.4mm;
    padding: 0;
    color: #4F4B47;
    font-size: 9pt;
    line-height: 1.55;
    break-inside: avoid;
}

.sources-appendix a {
    color: #4F4B47;
    font-weight: 400;
    text-decoration: underline;
    text-decoration-color: #B8B0A8;
    text-underline-offset: 1.5pt;
}

.sources-appendix a[href^="http"]::after {
    content: attr(href);
    display: block;
    margin-top: 0.4mm;
    color: #8A847E;
    font-size: 7.4pt;
    font-weight: 400;
    line-height: 1.35;
    text-decoration: none;
    overflow-wrap: anywhere;
    word-break: break-all;
}

.tool-signature {
    margin-top: 7mm;
    padding-top: 3.5mm;
    border-top: 0.8pt solid #DEDAD3;
    color: #77736E;
    font-size: 8.2pt;
    line-height: 1.5;
    break-inside: avoid;
}

.tool-signature p {
    margin: 0.8mm 0;
    color: #77736E;
}

.tool-signature a {
    color: #77736E;
    text-decoration: underline;
}

"""


MACOS_CHROME_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
)

CHROME_COMMANDS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "msedge",
)


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)


def strip_inline_markdown(value: str) -> str:
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    return html.unescape(value).strip()


def escape_css_content(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def extract_title_and_meta(md_text: str) -> tuple[str, list[tuple[str, str]], str]:
    """Extract the first H1 and its adjacent metadata quote for the cover."""
    lines = strip_frontmatter(md_text).splitlines()
    title = "商品销售战略报告"
    title_index = None
    for index, line in enumerate(lines):
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            title = strip_inline_markdown(match.group(1))
            title_index = index
            break

    if title_index is not None:
        del lines[title_index]

    meta: list[tuple[str, str]] = []
    scan = title_index if title_index is not None else 0
    while scan < len(lines) and not lines[scan].strip():
        scan += 1
    if scan < len(lines) and lines[scan].lstrip().startswith(">"):
        end = scan
        quote_lines: list[str] = []
        while end < len(lines) and (lines[end].lstrip().startswith(">") or not lines[end].strip()):
            if lines[end].lstrip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[end]).rstrip())
            end += 1
        for item in quote_lines:
            if "：" in item:
                label, value = item.split("：", 1)
                meta.append((label.strip(), value.strip()))
            elif ":" in item:
                label, value = item.split(":", 1)
                meta.append((label.strip(), value.strip()))
            elif item.strip():
                meta.append(("", item.strip()))
        del lines[scan:end]

    while lines and (not lines[0].strip() or lines[0].strip() == "---"):
        lines.pop(0)
    return title, meta, "\n".join(lines)


def add_table_classes(html_body: str) -> str:
    def replace_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        head = re.search(r"<thead>.*?</thead>", table_html, flags=re.S)
        columns = len(re.findall(r"<th(?:\s[^>]*)?>", head.group(0))) if head else 0
        class_name = f' class="cols-{min(max(columns, 1), 8)}"'
        return table_html.replace("<table>", f"<table{class_name}>", 1)

    return re.sub(r"<table>.*?</table>", replace_table, html_body, flags=re.S)


def wrap_sources_appendix(html_body: str) -> str:
    """Give the source appendix a quieter visual hierarchy than report chapters."""
    match = re.search(
        r'(<h1\s+id="[^"]+">\s*主要资料来源.*?</h1>)',
        html_body,
        flags=re.S,
    )
    if not match:
        return html_body
    return (
        html_body[: match.start()]
        + '<section class="sources-appendix">'
        + html_body[match.start() :]
        + "</section>"
    )


def add_markdown_heading_ids(md_text: str) -> tuple[str, list[tuple[str, str]]]:
    """Add stable anchors to reader-visible top-level headings only.

    A Markdown heading inside a blockquote begins with ``>`` and is therefore
    intentionally excluded.  This prevents campaign hooks such as ``> # ...``
    from becoming report chapters or reading-guide entries.
    """
    guide: list[tuple[str, str]] = []
    first_h1_seen = False
    counter = 0
    output: list[str] = []
    for line in md_text.splitlines():
        match = re.match(r"^(#{1,2})\s+(.+?)\s*$", line)
        if not match:
            output.append(line)
            continue
        level = len(match.group(1))
        include = level == 1 or (level == 2 and not first_h1_seen)
        if level == 1:
            first_h1_seen = True
        if not include:
            output.append(line)
            continue
        counter += 1
        anchor = f"section-{counter}"
        label = strip_inline_markdown(match.group(2))
        guide.append((anchor, label))
        output.append(f"{match.group(1)} {match.group(2)} {{#{anchor}}}")
    return "\n".join(output), guide


def meta_html(meta: list[tuple[str, str]]) -> str:
    rows = []
    for label, value in meta:
        label_html = html.escape(label + "：" if label else "")
        rows.append(
            '<div class="cover-meta-row">'
            f'<div class="cover-meta-label">{label_html}</div>'
            f'<div>{html.escape(value)}</div>'
            "</div>"
        )
    return "\n".join(rows)


def build_signature_html() -> str:
    """Return the fixed eCommerce-helper author colophon.

    The report author passed through ``--author`` and the Skill author are two
    different identities. The former belongs on the cover; this colophon
    credits the creator and maintainer of the rendering Skill.
    """
    return """
<section class="tool-signature">
  <p>本报告由 eCommerce-helper skill 工具协助生成</p>
  <p>Skill 设计与维护：嘉然 Jiaran</p>
  <p>交流和建议可联系作者：嘉然 Jiaran（+v: evadebot）</p>
  <p>个人网站：<a href="https://c.aoao.ai">https://c.aoao.ai</a></p>
</section>
"""


def build_html(
    md_text: str,
    title_override: str = "",
    subtitle: str = "",
    author: str = "",
    report_date: str = "",
) -> tuple[str, str]:
    import markdown

    extracted_title, meta, body_md = extract_title_and_meta(md_text)
    title = title_override.strip() or extracted_title
    body_md, guide = add_markdown_heading_ids(body_md)
    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists", "attr_list"],
        output_format="html5",
    )
    html_body = add_table_classes(html_body)
    html_body = wrap_sources_appendix(html_body)

    if not report_date:
        report_date = date.today().isoformat()
    footer_parts = [part for part in (report_date, author) if part]
    cover_footer = " · ".join(html.escape(part) for part in footer_parts)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    cover_subtitle = f'<div class="cover-subtitle">{safe_subtitle}</div>' if subtitle else ""
    cover_meta = f'<div class="cover-meta">{meta_html(meta)}</div>' if meta else ""
    footer = f'<div class="cover-footer">{cover_footer}</div>' if cover_footer else ""

    toc_items = "\n".join(
        f'<li><a href="#{anchor}">{html.escape(label)}</a></li>' for anchor, label in guide
    )
    guide_html = ""
    if toc_items:
        guide_html = f"""
<section class="reading-guide">
  <div class="guide-label">READING GUIDE</div>
  <h1>阅读导航</h1>
  <p class="guide-note">从结论进入，再依次查看产品机会、购买人群、销售主张、SKU 与价格、执行路径和最终决策。</p>
  <ol class="toc">{toc_items}</ol>
</section>
"""

    signature_html = build_signature_html()

    short_title = re.sub(r"\s*[（(][^）)]*[）)]\s*$", "", title).strip()
    header_text = f"{short_title}  |  商品销售战略报告"
    css = CSS_TEMPLATE.replace("FONT_STACK", FONT_STACK).replace(
        "HEADER_TEXT", escape_css_content(header_text)
    )
    document = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>{css}</style>
</head>
<body>
  <section class="cover">
    <div class="cover-eyebrow">ECOMMERCE STRATEGY REPORT</div>
    <div class="cover-title">{safe_title}</div>
    {cover_subtitle}
    <hr class="cover-divider">
    {cover_meta}
    {footer}
  </section>
  {guide_html}
  <main class="report-body">{html_body}{signature_html}</main>
</body>
</html>
"""
    return document, title


def find_chrome(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    env_path = os.environ.get("ECOMMERCE_HELPER_CHROME", "").strip()
    if env_path and Path(env_path).exists():
        return Path(env_path)
    for command in CHROME_COMMANDS:
        resolved = shutil.which(command)
        if resolved:
            return Path(resolved)
    for path in MACOS_CHROME_PATHS:
        if path.exists():
            return path
    windows_roots = [
        os.environ.get("PROGRAMFILES", ""),
        os.environ.get("PROGRAMFILES(X86)", ""),
        os.environ.get("LOCALAPPDATA", ""),
    ]
    windows_suffixes = (
        Path("Google/Chrome/Application/chrome.exe"),
        Path("Chromium/Application/chrome.exe"),
        Path("Microsoft/Edge/Application/msedge.exe"),
    )
    for root in filter(None, windows_roots):
        for suffix in windows_suffixes:
            candidate = Path(root) / suffix
            if candidate.exists():
                return candidate
    return None


def render_with_chrome(html_path: Path, output_path: Path, chrome: Path) -> bool:
    command = [
        str(chrome),
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_path}",
        html_path.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=os.sys.stderr)
    return result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0


def render_with_weasyprint(html_path: Path, output_path: Path) -> bool:
    try:
        from weasyprint import HTML

        HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(str(output_path))
        return output_path.exists() and output_path.stat().st_size > 0
    except Exception as exc:  # pragma: no cover - depends on local native libraries
        print(f"[WARN] WeasyPrint 不可用：{exc}", file=os.sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="将商品销售战略 Markdown 导出为报告级 PDF")
    parser.add_argument("input", type=Path, help="输入 Markdown 文件")
    parser.add_argument("output", type=Path, help="输出 PDF 文件")
    parser.add_argument("--title", default="", help="覆盖封面标题")
    parser.add_argument("--subtitle", default="中国市场新品销售策略", help="封面副标题")
    parser.add_argument("--author", default="", help="可选署名")
    parser.add_argument("--date", default="", help="封面日期，默认当天")
    parser.add_argument("--engine", choices=("auto", "chrome", "weasyprint"), default="auto")
    parser.add_argument("--chrome", type=Path, help="Chrome／Chromium 可执行文件")
    parser.add_argument("--html-output", type=Path, help="指定中间 HTML 路径")
    parser.add_argument("--keep-html", action="store_true", help="保留中间 HTML")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"输入文件不存在：{args.input}")

    md_text = args.input.read_text(encoding="utf-8")
    document, title = build_html(
        md_text,
        title_override=args.title,
        subtitle=args.subtitle,
        author=args.author,
        report_date=args.date,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.html_output:
        html_path = args.html_output
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_is_temporary = False
    else:
        descriptor, tmp_name = tempfile.mkstemp(prefix=f"{args.output.stem}-", suffix=".html")
        os.close(descriptor)
        html_path = Path(tmp_name)
        html_is_temporary = True
    html_path.write_text(document, encoding="utf-8")

    engine_used = ""
    success = False
    chrome = find_chrome(args.chrome)
    if args.engine in ("auto", "chrome") and chrome:
        success = render_with_chrome(html_path, args.output, chrome)
        if success:
            engine_used = "Chrome"
    elif args.engine == "chrome":
        print("[ERROR] 未找到 Chrome／Chromium。", file=os.sys.stderr)

    if not success and args.engine in ("auto", "weasyprint"):
        success = render_with_weasyprint(html_path, args.output)
        if success:
            engine_used = "WeasyPrint"

    if html_is_temporary and not args.keep_html:
        html_path.unlink(missing_ok=True)
    elif args.keep_html or args.html_output:
        print(f"[OK] HTML：{html_path}")

    if not success:
        print("[ERROR] PDF 渲染失败。请安装 Chrome，或补齐 WeasyPrint 原生依赖。", file=os.sys.stderr)
        return 1

    print(f"[OK] PDF：{args.output}")
    print(f"[OK] 标题：{title}")
    print(f"[OK] 渲染引擎：{engine_used}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
