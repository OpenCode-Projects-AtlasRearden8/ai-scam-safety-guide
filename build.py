#!/usr/bin/env python3
"""Build the static HTML site for The AI Scam Safety Guide.

Converts the Markdown files in docs/ into a self-contained static HTML site
in site/. Standard library only - nothing to install, nothing to configure,
works offline.

Usage:
    python3 build.py            # build into ./site
    python3 build.py --out DIR  # build somewhere else (used by tests)

Copyright (c) 2026 Asdale Dynamics, LLC - MIT License
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = ROOT / "assets"
DEFAULT_OUT = ROOT / "site"

SITE_TITLE = "The AI Scam Safety Guide"
SITE_TAGLINE = "Scams now come with perfect grammar, real hands and your own voice. Here is your manual."
SITE_DESCRIPTION = (
    "A beginner's manual for staying safe in the AI age: AI-written scam "
    "messages, deepfake photos, cloned-voice calls, fake AI tool sites, "
    "too-good deals, verifying people and payments, and a gentle recovery "
    "path if you already fell for one. From Asdale Dynamics, LLC."
)
COPYRIGHT = "Copyright (c) 2026 Asdale Dynamics, LLC"

NAV_OVERRIDES = {
    "index": "Start here",
    "checklist": "The Checklist",
    "stories": "Story Examples",
    "glossary": "Glossary",
}


# ---------------------------------------------------------------------------
# Inline markdown
# ---------------------------------------------------------------------------

_RE_CODE = re.compile(r"`([^`]+)`")
_RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_RE_BOLD = re.compile(r"\*\*(.+?)\*\*")
_RE_ITALIC = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
_RE_INTERNAL_MD = re.compile(r"^([A-Za-z0-9._/-]+)\.md(#[A-Za-z0-9-]+)?$")
_RE_EXTERNAL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://|^/")


def slugify(text: str) -> str:
    """Stable anchor id from heading text."""
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("'", "").replace("\u2019", "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "section"


def strip_inline(text: str) -> str:
    """Remove markdown marks so headings can be used as plain-text titles."""
    return re.sub(r"[*`_]", "", text).strip()


def _rewrite_href(href: str) -> str:
    m = _RE_INTERNAL_MD.match(href)
    if m:
        return f"{m.group(1)}.html{m.group(2) or ''}"
    return href


def inline(text: str) -> str:
    """Convert code spans, links, bold and italics in one line of markdown."""
    text = html.escape(text, quote=False)
    stashed: list[str] = []

    def _stash_code(m: re.Match) -> str:
        stashed.append(f"<code>{m.group(1)}</code>")
        return f"\x00C{len(stashed) - 1}\x00"

    text = _RE_CODE.sub(_stash_code, text)

    def _make_link(m: re.Match) -> str:
        label, href = m.group(1), _rewrite_href(m.group(2))
        if _RE_EXTERNAL.match(href):
            return f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'
        return f'<a href="{href}">{label}</a>'

    text = _RE_LINK.sub(_make_link, text)
    text = _RE_BOLD.sub(r"<strong>\1</strong>", text)
    text = _RE_ITALIC.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00C(\d+)\x00", lambda m: stashed[int(m.group(1))], text)


# ---------------------------------------------------------------------------
# Block markdown
# ---------------------------------------------------------------------------

_RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_RE_FENCE = re.compile(r"^(?:`{3,}|~{3,})\s*([^`]*)$")
_RE_HR = re.compile(r"^\s{0,3}(?:(-{3,}|\*{3,}|_{3,}))\s*$")
_RE_ULIST = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_RE_OLIST = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_RE_TASK = re.compile(r"^\[([ xX])\]\s+(.*)$")
_RE_QUOTE = re.compile(r"^\s*>")
_RE_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _list_sig(line: str) -> tuple[str, str, int] | tuple[None, None, int]:
    for pat, kind in ((_RE_ULIST, "ul"), (_RE_OLIST, "ol")):
        m = pat.match(line)
        if m:
            return kind, m.group(2), len(m.group(1))
    return None, None, 0


def _split_row(line: str) -> list[str]:
    line = line.strip().strip("|")
    parts = line.split("|")
    return [p.strip().replace("\\|", "|") for p in parts]


def _table(lines: list[str], i: int) -> tuple[str, int]:
    head = _split_row(lines[i])
    i += 2
    body: list[str] = []
    while i < len(lines) and "|" in lines[i] and lines[i].strip():
        cells = _split_row(lines[i])
        body.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
        i += 1
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    return (
        "<table>\n<thead><tr>" + th + "</tr></thead>\n<tbody>\n"
        + "\n".join(body) + "\n</tbody>\n</table>"
    ), i


def _list(lines: list[str], i: int, indent: int) -> tuple[str, int]:
    ordered = bool(_RE_OLIST.match(lines[i]))
    parts: list[tuple[str, str | None, list[str]]] = []

    while i < len(lines):
        if not lines[i].strip():
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and _list_sig(lines[j])[2] >= indent:
                i = j
                continue
            break

        kind, text, ind = _list_sig(lines[i])
        if kind is None or ind < indent or bool(ordered) != (kind == "ol"):
            break

        i += 1
        task: str | None = None
        m = _RE_TASK.match(text)
        if m and not ordered:
            task = " checked" if m.group(1) in "xX" else ""
            text = m.group(2)
        subs: list[str] = []
        while i < len(lines) and lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) > indent:
            subs.append(lines[i])
            i += 1
        if subs:
            if _list_sig(subs[0])[0]:
                sub_html, _ = _list(subs, 0, len(subs[0]) - len(subs[0].lstrip()))
                subs = [sub_html]
            else:
                joined = inline(" ".join(s.strip() for s in subs))
                subs = [f"<p>{joined}</p>"]
        parts.append((text, task, subs))

    tag = "ol" if ordered else "ul"
    out = []
    for text, task, subs in parts:
        if task is not None:
            inner = f'<input type="checkbox"{task}> {inline(text)}'
            out.append(f'<li class="task">{inner}{"".join(chr(10) + s for s in subs)}</li>')
        else:
            inner = inline(text) + "".join("\n" + s for s in subs)
            out.append(f"<li>{inner}</li>")
    return f"<{tag}>\n" + "\n".join(out) + f"\n</{tag}>", i


def _fence(lines: list[str], i: int) -> tuple[str, int]:
    m = _RE_FENCE.match(lines[i])
    info = re.sub(r"[^A-Za-z0-9-]", "", m.group(1) or "")
    i += 1
    body: list[str] = []
    while i < len(lines) and not _RE_FENCE.match(lines[i]):
        body.append(lines[i])
        i += 1
    if i < len(lines):
        i += 1
    cls = f' class="language-{info}"' if info else ""
    return f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>", i


def _blockquote(lines: list[str], i: int) -> tuple[str, int]:
    buf: list[str] = []
    while i < len(lines) and _RE_QUOTE.match(lines[i]):
        buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
        i += 1
    return "<blockquote>\n" + md_to_html("\n".join(buf)) + "\n</blockquote>", i


def _heading(lines: list[str], i: int) -> tuple[str, int]:
    m = _RE_HEADING.match(lines[i])
    level, text = len(m.group(1)), m.group(2).strip()
    anchor = slugify(strip_inline(text))
    return f'<h{level} id="{anchor}">{inline(text)}</h{level}>', i + 1


def _is_block_boundary(line: str) -> bool:
    if not line.strip():
        return True
    if _RE_FENCE.match(line) or _RE_HEADING.match(line) or _RE_HR.match(line):
        return True
    if _RE_QUOTE.match(line):
        return True
    kind, _, ind = _list_sig(line)
    if kind and ind < 4:
        return True
    return False


def _paragraph(lines: list[str], i: int) -> tuple[str, int]:
    buf = [lines[i].strip()]
    i += 1
    while i < len(lines) and lines[i].strip() and not _is_block_boundary(lines[i]):
        buf.append(lines[i].strip())
        i += 1
    return "<p>" + inline(" ".join(buf)) + "</p>", i


def md_to_html(md: str) -> str:
    """Convert the docs' Markdown subset into HTML."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif _RE_FENCE.match(line):
            block, i = _fence(lines, i)
            out.append(block)
        elif _RE_HEADING.match(line):
            block, i = _heading(lines, i)
            out.append(block)
        elif _RE_HR.match(line):
            out.append("<hr>")
            i += 1
        elif _RE_QUOTE.match(line):
            block, i = _blockquote(lines, i)
            out.append(block)
        elif "|" in lines[i] and i + 1 < len(lines) and _RE_TABLE_SEP.match(lines[i + 1]):
            block, i = _table(lines, i)
            out.append(block)
        elif _list_sig(line)[0] and (len(line) - len(line.lstrip())) < 4:
            block, i = _list(lines, i, len(line) - len(line.lstrip()))
            out.append(block)
        else:
            block, i = _paragraph(lines, i)
            out.append(block)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Site assembly
# ---------------------------------------------------------------------------

def first_h1(md: str) -> str | None:
    for line in md.split("\n"):
        m = _RE_HEADING.match(line)
        if m and len(m.group(1)) == 1:
            return strip_inline(m.group(2))
    return None


def page_title_for(stem: str, title: str) -> str:
    if stem in NAV_OVERRIDES:
        return NAV_OVERRIDES[stem]
    return re.sub(r"^\d+[\s-]+", "", title)


def read_pages() -> list[dict]:
    paths = sorted(DOCS_DIR.glob("*.md"), key=lambda p: (p.name != "index.md", p.name))
    pages = []
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        title = first_h1(raw) or f"Untitled ({path.stem})"
        pages.append({
            "slug": path.stem,
            "file": path.stem + ".html",
            "title": title,
            "label": page_title_for(path.stem, title),
            "body": md_to_html(raw),
        })
    return pages


def render_page(page: dict, pages: list[dict], index: int) -> str:
    nav_items: list[str] = []
    for p in pages:
        current = ' aria-current="page"' if p["slug"] == page["slug"] else ""
        nav_items.append(
            f'<li><a href="{p["file"]}"{current}>{html.escape(p["label"])}</a></li>'
        )
    nav = "\n".join(nav_items)

    prev_html = ""
    if index > 0:
        p = pages[index - 1]
        prev_html = (
            f'<a class="prev" href="{p["file"]}"><span class="dir">Previous</span>'
            f"{html.escape(p['label'])}</a>"
        )
    next_html = ""
    if index + 1 < len(pages):
        p = pages[index + 1]
        next_html = (
            f'<a class="next" href="{p["file"]}"><span class="dir">Next</span>'
            f"{html.escape(p['label'])}</a>"
        )

    print_row = ""
    if page["slug"] == "checklist":
        print_row = (
            '<div class="print-row">'
            '<button class="print-button" onclick="window.print()">Print the checklist</button>'
            '<span class="hint">or press Ctrl+P (Cmd+P on a Mac)</span></div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(SITE_DESCRIPTION, quote=True)}">
<title>{html.escape(page["title"])} | {SITE_TITLE}</title>
<link rel="icon" href="favicon.svg">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="wrap">
<header class="site-header">
<p class="kicker">Asdale Dynamics, LLC &middot; Beginner Guides</p>
<h1 class="site-title"><a href="index.html">{SITE_TITLE}</a></h1>
<p class="tagline">{SITE_TAGLINE}</p>
</header>
<nav class="site-nav" aria-label="Chapters">
<ul>
{nav}
</ul>
</nav>
<article>
{print_row}
{page["body"]}
</article>
<nav class="prevnext" aria-label="Adjacent chapters">
{prev_html}{next_html}
</nav>
<footer class="site-footer">
<p>{SITE_TITLE} is written and built by Asdale Dynamics, LLC. {COPYRIGHT}.</p>
<p>Licensed under the MIT License. Plain static HTML: no analytics, no cookies, no tracking, and it works offline.</p>
</footer>
</div>
</body>
</html>
"""


def build(out_dir: Path = DEFAULT_OUT) -> list[str]:
    """Build the site into out_dir; return the files written."""
    out_dir = Path(out_dir).resolve()
    if out_dir in (Path("/"), ROOT) or out_dir == ROOT.parent:
        raise ValueError(f"Refusing to build into unsafe location: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    pages = read_pages()
    written: list[str] = []
    for idx, page in enumerate(pages):
        target = out_dir / page["file"]
        target.write_text(render_page(page, pages, idx), encoding="utf-8")
        written.append(page["file"])

    for asset in sorted(ASSETS_DIR.iterdir()):
        if asset.is_file():
            shutil.copy2(asset, out_dir / asset.name)
            written.append(asset.name)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the guide's static site.")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="output directory (default: site/)")
    args = parser.parse_args()
    out = Path(args.out)
    files = build(out)
    print(f"Built {len(files)} files into {out}/")
    for f in files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
