#!/usr/bin/env python3
"""
Build the static site for this repository (GitHub Pages).

Everything on the site is generated from the repository itself, so the site
stays in sync with the code with zero manual editing:

  * the root README.md is rendered on the home page,
  * every top-level folder becomes a project page,
  * every source file gets a syntax-highlighted reader page,
  * folders without a README get one generated automatically,
  * the root README gets an auto-maintained project index.

Usage:
    python3 scripts/build_site.py                # build into _site/
    python3 scripts/build_site.py --out _site    # same, explicit
    python3 scripts/build_site.py --no-readme    # do not touch README files
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

SKIP_DIRS = {".git", ".github", "_site", "node_modules", "__pycache__", ".idea",
             "scripts", "docs", ".vscode", "dist", "build", "site"}

SKIP_SUFFIXES = {".class", ".jar", ".zip", ".exe", ".dll", ".so", ".o"}

# files that are copied into the site as-is (so relative links keep working)
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
                  ".css", ".js", ".json", ".xml", ".txt", ".pdf", ".woff",
                  ".woff2", ".ttf", ".html", ".htm", ".csv"}

# files rendered as a code-reader page
CODE_SUFFIXES = {".java", ".py", ".js", ".html", ".css", ".md", ".json",
                 ".xml", ".sh", ".yml", ".yaml", ".c", ".cpp", ".h", ".sql",
                 ".txt"}

LANGUAGE_NAMES = {
    ".java": "Java", ".py": "Python", ".js": "JavaScript", ".html": "HTML",
    ".css": "CSS", ".md": "Markdown", ".json": "JSON", ".xml": "XML",
    ".sh": "Shell", ".yml": "YAML", ".yaml": "YAML", ".c": "C",
    ".cpp": "C++", ".h": "C header", ".sql": "SQL", ".txt": "Text",
    ".class": "Compiled class", ".png": "Image", ".jpg": "Image",
    ".jpeg": "Image", ".gif": "Image", ".svg": "Image", ".pdf": "PDF",
}

HIGHLIGHT_CLASS = {
    ".java": "java", ".py": "python", ".js": "javascript", ".html": "xml",
    ".css": "css", ".md": "markdown", ".json": "json", ".xml": "xml",
    ".sh": "bash", ".yml": "yaml", ".yaml": "yaml", ".c": "c",
    ".cpp": "cpp", ".h": "cpp", ".sql": "sql", ".txt": "plaintext",
}

GROUPS = [
    ("data", "Data Structures & Algorithms",
     "Labs on lists, stacks and other core data structures."),
    ("web", "Web Development",
     "HTML, CSS and the web-design exercises."),
    ("other", "Other work", "Everything else in the repository."),
]

LANG_IGNORE = {"Compiled class", "Markdown", "Image", "Text", "JSON", "PDF"}

BORING_RE = re.compile(r"(?i)^(course\s*:|faculty of|universiti|name\s*:|matric|program\s*:|lab\s*:|date\s*:|version\b)")

PROJECTS_START = "<!-- AUTO-GENERATED:PROJECTS:START -->"
PROJECTS_END = "<!-- AUTO-GENERATED:PROJECTS:END -->"
PROJECT_README_MARKER = "<!-- AUTO-GENERATED:PROJECT-README -->"

SITE_TITLE = "Seanneol · University Source Code"


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


def group_for(name: str) -> str:
    low = name.lower()
    if "web" in low or "html" in low or "css" in low:
        return "web"
    if "data structure" in low or "algorithm" in low:
        return "data"
    return "other"


def git_short_sha(root: Path) -> str:
    sha = os.environ.get("GITHUB_SHA", "")
    if not sha:
        try:
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                          stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            sha = ""
    return sha[:7]


def repo_url() -> str:
    return os.environ.get("GITHUB_REPOSITORY_URL", "").rstrip("/") or \
        "https://github.com/seanneol88/University-Source-Code"


def build_time() -> dt.datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return dt.datetime.fromtimestamp(int(epoch), dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


# --------------------------------------------------------------------------
# markdown
# --------------------------------------------------------------------------

def render_markdown(text: str) -> str:
    """Render markdown to HTML, with a tiny fallback when `markdown` is absent."""
    try:
        import markdown  # type: ignore
    except ImportError:
        return _fallback_markdown(text)

    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "sane_lists", "attr_list"],
        output_format="html5",
    )


def _fallback_markdown(text: str) -> str:
    out: list[str] = []
    in_code = False
    in_list = False
    for line in text.splitlines():
        if line.startswith("```"):
            if in_list:
                out.append("</ul>")
                in_list = False
            if in_code:
                out.append("</code></pre>")
            else:
                out.append("<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(esc(line))
            continue
        if re.match(r"^\s*[-*] ", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + _inline(line.strip()[2:]) + "</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if not line.strip():
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
        elif line.strip() in ("---", "***"):
            out.append("<hr />")
        else:
            out.append("<p>" + _inline(line.strip()) + "</p>")
    if in_list:
        out.append("</ul>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def _inline(text: str) -> str:
    # let simple raw HTML (badges, line breaks) through instead of escaping it
    tags: list[str] = []

    def stash_tag(match: re.Match) -> str:
        tags.append(match.group(0))
        return f"\x00TAG{len(tags) - 1}\x00"

    text = re.sub(r"</?[a-zA-Z][^>]*>", stash_tag, text)
    text = esc(text)
    text = re.sub(r"\x00TAG(\d+)\x00", lambda m: tags[int(m.group(1))], text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")
BADGE_RE = re.compile(r"\[!\[([^\]]*)\]\(([^)\s]+)\)\]\(([^)\s]+)\)")
AUTOLINK_RE = re.compile(r"<((?:https?://|mailto:)[^>\s]+)>")


def normalise_markdown(md: str) -> str:
    """Turn constructs the markdown engine cannot nest into plain HTML/links.

    * ``[![alt](img)](url)``  ->  <a href="url"><img src="img" alt="alt"></a>
    * ``<https://example.com>`` -> ``[https://example.com](https://example.com)``
    """
    md = BADGE_RE.sub(
        lambda m: f'<a href="{m.group(3)}"><img src="{m.group(2)}" alt="{html.escape(m.group(1))}"></a>',
        md)
    md = AUTOLINK_RE.sub(lambda m: f"[{m.group(1)}]({m.group(1)})", md)
    return md
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def rewrite_links(md: str, resolver) -> str:
    """Rewrite relative markdown links/images; skip inside fenced code blocks."""
    fenced: list[str] = []

    def stash(match: re.Match) -> str:
        fenced.append(match.group(0))
        return f"\x00FENCE{len(fenced) - 1}\x00"

    protected = FENCE_RE.sub(stash, normalise_markdown(md))

    def repl(match: re.Match) -> str:
        bang, label, target, title = match.group(1), match.group(2), match.group(3), match.group(4) or ""
        resolved = resolver(target, bool(bang))
        return f"{bang}[{label}]({resolved}{title})"

    protected = LINK_RE.sub(repl, protected)
    protected = re.sub(r"\x00FENCE(\d+)\x00", lambda m: fenced[int(m.group(1))], protected)
    return protected


def strip_heading(md: str) -> str:
    """Drop the first H1 so page titles are not duplicated."""
    match = HEADING_RE.search(md)
    if match and len(match.group(1)) == 1:
        return md[:match.start()] + md[match.end():]
    return md


# --------------------------------------------------------------------------
# repository scanning
# --------------------------------------------------------------------------

class Project:
    def __init__(self, path: Path, root: Path):
        self.path = path
        self.root = root
        self.name = path.name
        self.slug = slugify(path.name)
        self.group = group_for(path.name)
        self.files = sorted(
            (p for p in path.rglob("*")
             if p.is_file()
             and not any(part in SKIP_DIRS for part in p.relative_to(path).parts)),
            key=lambda p: (len(p.relative_to(path).parts), p.name.lower()),
        )
        self.readme = path / "README.md"

    @property
    def rel_files(self) -> list[Path]:
        return [p.relative_to(self.path) for p in self.files]

    def languages(self) -> list[str]:
        seen: list[str] = []
        for f in self.files:
            name = LANGUAGE_NAMES.get(f.suffix.lower())
            if name and name not in LANG_IGNORE and name not in seen:
                seen.append(name)
        return seen

    def line_count(self) -> int:
        total = 0
        for f in self.files:
            if f.suffix.lower() in CODE_SUFFIXES:
                try:
                    total += len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
                except OSError:
                    pass
        return total

    def summary(self) -> str:
        """First meaningful paragraph of the README, else one generated from the files."""
        if self.readme.exists():
            raw = self.readme.read_text(encoding="utf-8", errors="ignore")
            # never describe a folder using a README this script generated
            if not raw.lstrip().startswith(PROJECT_README_MARKER):
                return self._readme_summary(raw) or self.generated_summary()
        return self.generated_summary()

    def _readme_summary(self, text: str) -> str:
        if True:
            text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
            for block in text.split("\n\n"):
                block = block.strip()
                if not block or block.startswith(("#", "|", "```", "-", "*", ">", "!", "<")):
                    continue
                flat = re.sub(r"\s+", " ", block)
                if BORING_RE.search(flat) or len(flat) < 25:
                    continue
                return re.sub(r"[*_`]", "", flat)[:220]
        return ""

    def generated_summary(self) -> str:
        """A one-liner describing the folder, derived from the file names."""
        stems: list[str] = []
        for f in self.files:
            if f.suffix.lower() in (".java", ".py", ".js", ".html", ".css", ".c", ".cpp"):
                if f.stem not in stems:
                    stems.append(f.stem)
        langs = " / ".join(self.languages()) or "source"
        shown = ", ".join(stems[:5]) + (" …" if len(stems) > 5 else "")
        if stems:
            return f"{langs} coursework — {shown}."
        return f"{len(self.files)} file{'s' if len(self.files) != 1 else ''} of {langs} coursework."


def scan_projects(root: Path) -> list[Project]:
    projects = []
    for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if not any(p.is_file() for p in entry.rglob("*")):
            continue
        projects.append(Project(entry, root))
    return projects


# --------------------------------------------------------------------------
# generated README files
# --------------------------------------------------------------------------

def generated_project_readme(project: Project, site_base: str) -> str:
    langs = ", ".join(project.languages()) or "source files"
    rows = []
    for rel in project.rel_files:
        full = project.path / rel
        lang = LANGUAGE_NAMES.get(full.suffix.lower(), full.suffix.lstrip(".") or "file")
        lines = ""
        if full.suffix.lower() in CODE_SUFFIXES:
            try:
                lines = str(len(full.read_text(encoding="utf-8", errors="ignore").splitlines()))
            except OSError:
                lines = ""
        rows.append(f"| `{rel.as_posix()}` | {lang} | {lines} |")

    return f"""{PROJECT_README_MARKER}
# {project.name}

{project.summary()}

**Contents:** {len(project.files)} file(s) · {langs}

| File | Type | Lines |
| --- | --- | --- |
{chr(10).join(rows)}

---

*This README is generated automatically from the folder contents by
`scripts/build_site.py`. It is refreshed on every push to `main`, so the file
list above always matches what is in the folder. Everything in this folder is
also browsable on the site: {site_base}labs/{project.slug}/
"""


def update_root_readme(root: Path, projects: list[Project], site_url: str) -> bool:
    readme = root / "README.md"
    original = readme.read_text(encoding="utf-8") if readme.exists() else "# Hi 👋\n"

    rows = ["| Project | What it is | Files | Languages |", "| --- | --- | --- | --- |"]
    for p in projects:
        desc = p.summary().replace("|", "\\|")
        if len(desc) > 150:
            desc = desc[:147] + "…"
        langs = ", ".join(p.languages()) or "—"
        rows.append(f"| [{p.name}]({site_url}labs/{p.slug}/) | {desc} | {len(p.files)} | {langs} |")

    block = "\n".join([
        PROJECTS_START,
        "## 🗂️ Every project in this repository",
        "",
        "*Auto-generated by `scripts/build_site.py` from the repository contents — "
        "do not edit this table by hand, it is rewritten on every push to `main`.*",
        "",
        *rows,
        "",
        f"🌐 Browse all of it as a website: **{site_url}**",
        PROJECTS_END,
    ])

    if PROJECTS_START in original and PROJECTS_END in original:
        pattern = re.compile(re.escape(PROJECTS_START) + r".*?" + re.escape(PROJECTS_END), re.DOTALL)
        updated = pattern.sub(lambda _: block, original)
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"

    if updated != original:
        readme.write_text(updated, encoding="utf-8")
        return True
    return False


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

CSS = """
:root {
  --bg: #0b1020;
  --bg-soft: #111a33;
  --card: #141e3a;
  --card-hover: #1a2748;
  --border: #24304f;
  --text: #e8ecf8;
  --muted: #9aa6c4;
  --accent: #6ea8fe;
  --accent-2: #9d7bff;
  --accent-3: #35d0a5;
  --code-bg: #0d1428;
  --radius: 16px;
  --mono: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; background: var(--bg); color: var(--text); font-family: var(--sans);
  line-height: 1.65; -webkit-font-smoothing: antialiased;
  background-image:
    radial-gradient(900px 480px at 12% -8%, rgba(110,168,254,.20), transparent 60%),
    radial-gradient(760px 420px at 92% 0%, rgba(157,123,255,.18), transparent 55%),
    radial-gradient(700px 500px at 50% 108%, rgba(53,208,165,.10), transparent 60%);
  background-repeat: no-repeat; background-attachment: fixed; min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { max-width: 1040px; margin: 0 auto; padding: 0 20px; }

header.site {
  position: sticky; top: 0; z-index: 20; backdrop-filter: blur(14px);
  background: rgba(11,16,32,.72); border-bottom: 1px solid var(--border);
}
header.site .row { display: flex; align-items: center; gap: 16px; height: 62px; }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; color: var(--text); font-size: 1.02rem; }
.brand:hover { text-decoration: none; color: var(--accent); }
.dot { width: 10px; height: 10px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-2)); box-shadow: 0 0 14px rgba(110,168,254,.8); }
header.site nav { margin-left: auto; display: flex; gap: 6px; flex-wrap: wrap; }
header.site nav a { color: var(--muted); padding: 7px 12px; border-radius: 9px; font-size: .9rem; }
header.site nav a:hover { color: var(--text); background: var(--card-hover); text-decoration: none; }

.hero { padding: 62px 0 20px; }
.eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: .78rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--accent-3); border: 1px solid var(--border);
  background: rgba(53,208,165,.08); padding: 5px 12px; border-radius: 999px; }
h1.title { font-size: clamp(2rem, 5vw, 3.1rem); line-height: 1.12; margin: 18px 0 12px; letter-spacing: -.02em; }
h1.title .grad { background: linear-gradient(100deg, var(--accent), var(--accent-2) 55%, var(--accent-3));
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.lede { color: var(--muted); font-size: 1.07rem; max-width: 62ch; margin: 0; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 30px 0 8px; }
.stat { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 18px; }
.stat b { display: block; font-size: 1.55rem; letter-spacing: -.02em; }
.stat span { color: var(--muted); font-size: .84rem; text-transform: uppercase; letter-spacing: .08em; }

section { padding: 34px 0; }
h2.sec { font-size: .82rem; letter-spacing: .16em; text-transform: uppercase; color: var(--muted);
  margin: 0 0 16px; font-weight: 700; }
h3.group { font-size: 1.05rem; margin: 26px 0 12px; color: var(--text); }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(288px, 1fr)); gap: 16px; }
.card { display: block; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px; color: var(--text); transition: .18s ease; position: relative; overflow: hidden; }
.card:before { content: ""; position: absolute; inset: 0 0 auto 0; height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2)); opacity: 0; transition: .18s; }
.card:hover { background: var(--card-hover); transform: translateY(-3px); text-decoration: none;
  border-color: #33436e; box-shadow: 0 18px 40px -24px rgba(0,0,0,.9); }
.card:hover:before { opacity: 1; }
.card h4 { margin: 0 0 8px; font-size: 1.06rem; }
.card p { margin: 0 0 14px; color: var(--muted); font-size: .92rem; display: -webkit-box;
  -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.card .meta { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { font-size: .74rem; color: var(--muted); border: 1px solid var(--border);
  background: rgba(255,255,255,.02); padding: 3px 9px; border-radius: 999px; }
.tag.lang { color: var(--accent); border-color: rgba(110,168,254,.35); }

.panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 26px 28px; }
.prose > :first-child { margin-top: 0; }
.prose h1, .prose h2, .prose h3, .prose h4 { line-height: 1.25; margin: 1.5em 0 .55em; letter-spacing: -.01em; }
.prose h1 { font-size: 1.8rem; }
.prose h2 { font-size: 1.32rem; border-bottom: 1px solid var(--border); padding-bottom: .3em; }
.prose h3 { font-size: 1.1rem; }
.prose p, .prose li { color: #cfd8ee; }
.prose ul, .prose ol { padding-left: 1.3em; }
.prose li { margin: .3em 0; }
.prose code { font-family: var(--mono); font-size: .87em; background: var(--code-bg);
  border: 1px solid var(--border); border-radius: 6px; padding: .12em .4em; color: #cfe3ff; }
.prose pre { background: var(--code-bg); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px 18px; overflow-x: auto; }
.prose pre code { background: none; border: 0; padding: 0; font-size: .87rem; }
.prose table { width: 100%; border-collapse: collapse; margin: 1.1em 0; font-size: .92rem; display: block; overflow-x: auto; }
.prose th, .prose td { border: 1px solid var(--border); padding: 9px 12px; text-align: left; vertical-align: top; }
.prose th { background: var(--bg-soft); }
.prose blockquote { margin: 1.2em 0; padding: .6em 1em; border-left: 3px solid var(--accent);
  background: rgba(110,168,254,.07); border-radius: 0 10px 10px 0; color: var(--muted); }
.prose img { max-width: 100%; border-radius: 10px; border: 1px solid var(--border); vertical-align: middle; }
.prose hr { border: 0; border-top: 1px solid var(--border); margin: 2em 0; }

.crumbs { color: var(--muted); font-size: .88rem; padding: 26px 0 0; }
.crumbs a { color: var(--muted); }
.crumbs a:hover { color: var(--accent); }

.page-head { padding: 14px 0 4px; }
.page-head h1 { font-size: clamp(1.6rem, 4vw, 2.3rem); margin: 8px 0 10px; letter-spacing: -.02em; }
.page-head p { color: var(--muted); margin: 0 0 14px; max-width: 70ch; }
.btnrow { display: flex; gap: 10px; flex-wrap: wrap; margin: 18px 0 0; }
.btn { display: inline-flex; align-items: center; gap: 8px; border-radius: 10px; padding: 9px 15px;
  border: 1px solid var(--border); color: var(--text); background: var(--bg-soft); font-size: .9rem; }
.btn:hover { background: var(--card-hover); text-decoration: none; border-color: #33436e; }
.btn.primary { background: linear-gradient(120deg, var(--accent), var(--accent-2)); border: 0; color: #08101f; font-weight: 650; }

.filelist { display: grid; gap: 8px; }
.file { display: flex; align-items: center; gap: 12px; background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 12px 16px; color: var(--text); }
.file:hover { background: var(--card-hover); text-decoration: none; border-color: #33436e; }
.file .fname { font-family: var(--mono); font-size: .92rem; }
.file .fmeta { margin-left: auto; color: var(--muted); font-size: .8rem; white-space: nowrap; }
.file.plain { opacity: .72; }

.codehead { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.codehead .fname { font-family: var(--mono); font-size: 1rem; }
.code-wrap { position: relative; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: var(--code-bg); }
.code-wrap pre { margin: 0; padding: 18px 16px; overflow-x: auto; font-family: var(--mono);
  font-size: .86rem; line-height: 1.62; }
.code-wrap code { font-family: inherit; }
.code-inner { display: flex; align-items: stretch; }
.code-inner pre { margin: 0; font-family: var(--mono); font-size: .86rem; line-height: 1.62; }
.code-inner pre.gutter { padding: 18px 14px 18px 16px; text-align: right; color: #4a5a80;
  user-select: none; border-right: 1px solid var(--border); font-variant-numeric: tabular-nums; }
.code-inner pre.code { flex: 1; padding: 18px 16px; overflow-x: auto; }
.code-inner pre.code code { font-family: inherit; background: none; border: 0; padding: 0; }
.copy { position: absolute; top: 10px; right: 10px; background: var(--card); color: var(--muted);
  border: 1px solid var(--border); border-radius: 8px; font-size: .76rem; padding: 5px 10px; cursor: pointer; }
.copy:hover { color: var(--text); background: var(--card-hover); }

footer.site { border-top: 1px solid var(--border); margin-top: 40px; padding: 26px 0 40px;
  color: var(--muted); font-size: .88rem; }
footer.site .row { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }
footer.site .spacer { margin-left: auto; }

.empty { color: var(--muted); font-style: italic; }
.blurb { color: var(--muted); font-size: .9rem; margin: -8px 0 16px; }
@media (max-width: 640px) {
  .hero { padding: 40px 0 10px; }
  .panel { padding: 20px 18px; }
  header.site nav a { padding: 6px 8px; font-size: .84rem; }
}
"""

COPY_JS = """
document.querySelectorAll('.copy').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var pre = btn.closest('.code-wrap').querySelector('pre.code');
    navigator.clipboard.writeText(pre.innerText).then(function () {
      var old = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = old; }, 1400);
    });
  });
});
"""


def page(title: str, body: str, depth: int, nav: list[tuple[str, str]] | None = None,
         description: str = "", code_highlight: bool = False, commit: str = "") -> str:
    prefix = "../" * depth
    nav_html = "".join(f'<a href="{prefix}{href}">{esc(label)}</a>' for label, href in (nav or []))
    hl_head = (
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/'
        'github-dark.min.css">\n'
        '<script defer src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>\n'
        '<script defer src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/java.min.js"></script>\n'
        '<script>window.addEventListener("DOMContentLoaded",function(){if(window.hljs){'
        'document.querySelectorAll("pre code").forEach(function(el){hljs.highlightElement(el);});}});</script>'
    ) if code_highlight else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description or SITE_TITLE)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description or SITE_TITLE)}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💻</text></svg>">
<style>{CSS}</style>
{hl_head}
</head>
<body>
<header class="site"><div class="wrap row">
  <a class="brand" href="{prefix}index.html"><span class="dot"></span>{esc(SITE_TITLE)}</a>
  <nav>{nav_html}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap row">
  <span>© {build_time():%Y} Seanneol · built from the repository{f" @ <code>{esc(commit)}</code>" if commit else ""}</span>
  <span class="spacer"></span>
  <a href="{repo_url()}">Source on GitHub ↗</a>
</div></footer>
<script>{COPY_JS}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# site builder
# --------------------------------------------------------------------------

class SiteBuilder:
    def __init__(self, root: Path, out: Path):
        self.root = root
        self.out = out
        self.projects = scan_projects(root)
        self.by_name = {p.name: p for p in self.projects}
        self.commit = git_short_sha(root)
        self.site_prefix = "https://%s.github.io/%s/" % (
            (os.environ.get("GITHUB_REPOSITORY", "seanneol88/University-Source-Code").split("/")[0]),
            (os.environ.get("GITHUB_REPOSITORY", "seanneol88/University-Source-Code").split("/")[-1]),
        )
        if not os.environ.get("GITHUB_REPOSITORY"):
            self.site_prefix = "https://seanneol88.github.io/University-Source-Code/"

    # ---------- link resolution ----------

    def project_link(self, project: Project) -> str:
        return f"labs/{project.slug}/"

    def github_tree(self, project: Project) -> str:
        return f"{repo_url()}/tree/main/{quote(project.name)}"

    # ---------- pieces ----------

    def project_cards(self) -> str:
        parts = []
        for key, heading, blurb in GROUPS:
            items = [p for p in self.projects if p.group == key]
            if not items:
                continue
            cards = []
            for p in items:
                langs = "".join(f'<span class="tag lang">{esc(l)}</span>' for l in p.languages()[:4])
                summary = p.summary()
                if len(summary) > 160:
                    summary = summary[:157].rsplit(" ", 1)[0] + "…"
                cards.append(f"""<a class="card" href="{self.project_link(p)}index.html">
  <h4>{esc(p.name)}</h4>
  <p>{esc(summary)}</p>
  <div class="meta"><span class="tag">{len(p.files)} files</span>{langs}</div>
</a>""")
            parts.append(f'<h3 class="group">{esc(heading)}</h3>\n<p class="blurb">{esc(blurb)}</p>\n'
                         f'<div class="grid">{"".join(cards)}</div>')
        return "\n".join(parts) if parts else '<p class="empty">No projects yet.</p>'

    def nav(self) -> list[tuple[str, str]]:
        return [("Home", "index.html")] + [(p.name, f"labs/{p.slug}/index.html") for p in self.projects]

    # ---------- home ----------

    def build_home(self) -> None:
        readme_path = self.root / "README.md"
        readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        readme = re.sub(re.escape(PROJECTS_START) + r".*?" + re.escape(PROJECTS_END), "", readme,
                        flags=re.DOTALL)

        def resolver(target: str, is_image: bool) -> str:
            clean = target.split("#")[0].strip()
            if re.match(r"^(https?:|mailto:|#|//)", target) or not clean:
                return target
            name = clean.strip("/").replace("%20", " ")
            if name in self.by_name:
                return self.project_link(self.by_name[name]) + "index.html" + (
                    "#" + target.split("#", 1)[1] if "#" in target else "")
            if clean.lower().endswith(".md"):
                return repo_url() + "/blob/main/" + clean
            return repo_url() + "/blob/main/" + clean

        body_md = rewrite_links(strip_heading(readme), resolver)
        body_html = render_markdown(body_md)

        total_files = sum(len(p.files) for p in self.projects)
        total_lines = sum(p.line_count() for p in self.projects)
        langs = sorted({l for p in self.projects for l in p.languages()})

        hero = f"""<section class="hero">
  <span class="eyebrow">● University coursework · auto-published</span>
  <h1 class="title">Hi, I'm <span class="grad">Seanneol</span></h1>
  <p class="lede">Computer science student documenting labs in data structures and web design.
  Every project below is generated straight from the repository — the code, the READMEs and this
  page all update themselves on the next push.</p>
  <div class="stats">
    <div class="stat"><b>{len(self.projects)}</b><span>projects</span></div>
    <div class="stat"><b>{total_files}</b><span>files</span></div>
    <div class="stat"><b>{total_lines:,}</b><span>lines of code</span></div>
    <div class="stat"><b>{len(langs)}</b><span>languages</span></div>
  </div>
  <div class="btnrow">
    <a class="btn primary" href="#projects">Browse projects ↓</a>
    <a class="btn" href="{repo_url()}">GitHub repository ↗</a>
  </div>
</section>
<section id="projects">
  <h2 class="sec">Projects</h2>
  {self.project_cards()}
</section>
<section id="about">
  <h2 class="sec">About · from README.md</h2>
  <div class="panel prose">{body_html}</div>
</section>"""

        (self.out / "index.html").write_text(
            page(SITE_TITLE, hero, 0, self.nav(),
                 description="University lab source code: data structures, algorithms and web design.",
                 commit=self.commit),
            encoding="utf-8")

    # ---------- project pages ----------

    def build_project(self, project: Project) -> None:
        target = self.out / "labs" / project.slug
        target.mkdir(parents=True, exist_ok=True)

        # copy browser-friendly assets so relative links keep working
        for f in project.files:
            if f.suffix.lower() in ASSET_SUFFIXES:
                dest = target / f.relative_to(project.path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)

        def resolver(target_ref: str, is_image: bool) -> str:
            if re.match(r"^(https?:|mailto:|#|//)", target_ref) or not target_ref.strip():
                return target_ref
            path, _, anchor = target_ref.partition("#")
            suffix = "." + target_ref.split("?")[0].rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
            candidate = (project.path / path.replace("%20", " ")).resolve()
            if candidate.exists() and candidate.is_file():
                if suffix in CODE_SUFFIXES:
                    return path + ".html" + (("#" + anchor) if anchor else "")
                return path + (("#" + anchor) if anchor else "")
            return repo_url() + "/blob/main/" + (project.name + "/" + path).replace(" ", "%20")

        if project.readme.exists():
            md = project.readme.read_text(encoding="utf-8", errors="ignore")
            md = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
            content_html = render_markdown(rewrite_links(strip_heading(md), resolver))
        else:
            content_html = f"<p>{esc(project.summary())}</p>"

        files_html = []
        for rel in project.rel_files:
            full = project.path / rel
            suffix = full.suffix.lower()
            lang = LANGUAGE_NAMES.get(suffix, suffix.lstrip(".") or "file")
            if suffix in SKIP_SUFFIXES:
                files_html.append(f'<span class="file plain"><span class="fname">{esc(rel.as_posix())}</span>'
                                  f'<span class="fmeta">{esc(lang)} · binary</span></span>')
                continue
            href = f"{rel.as_posix()}.html" if suffix in CODE_SUFFIXES else rel.as_posix()
            note = ""
            if suffix in CODE_SUFFIXES:
                try:
                    note = f"{len(full.read_text(encoding='utf-8', errors='ignore').splitlines())} lines"
                except OSError:
                    note = ""
            files_html.append(f'<a class="file" href="{esc(href)}"><span class="fname">📄 {esc(rel.as_posix())}</span>'
                              f'<span class="fmeta">{esc(lang)}{" · " + note if note else ""}</span></a>')

        body = f"""<div class="crumbs"><a href="../../index.html">Home</a> / {esc(project.name)}</div>
<section class="page-head">
  <h1>{esc(project.name)}</h1>
  <p>{esc(project.summary())}</p>
  <div class="meta">
    <span class="tag">{len(project.files)} files</span>
    <span class="tag">{project.line_count():,} lines</span>
    {"".join(f'<span class="tag lang">{esc(l)}</span>' for l in project.languages())}
  </div>
  <div class="btnrow">
    <a class="btn" href="{self.github_tree(project)}">Folder on GitHub ↗</a>
    <a class="btn" href="#files">Files ↓</a>
  </div>
</section>
<section id="files">
  <h2 class="sec">Files</h2>
  <div class="filelist">{"".join(files_html)}</div>
</section>
<section id="readme">
  <h2 class="sec">README</h2>
  <div class="panel prose">{content_html}</div>
</section>"""

        (target / "index.html").write_text(
            page(f"{project.name} · {SITE_TITLE}", body, 2, self.nav(),
                 description=project.summary(), commit=self.commit),
            encoding="utf-8")

    # ---------- code reader pages ----------

    def build_code_page(self, project: Project, rel: Path) -> None:
        full = project.path / rel
        try:
            source = full.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return
        lines = source.splitlines()
        lang = HIGHLIGHT_CLASS.get(full.suffix.lower(), "plaintext")
        gutter = "\n".join(str(i + 1) for i in range(len(lines)))
        depth = 2          # labs/<slug>/<file>.html is two levels below the site root
        rel_href = rel.as_posix()
        preview = ""
        if full.suffix.lower() == ".html":
            preview = f'<a class="btn" href="{esc(rel_href)}" target="_blank" rel="noopener">Live preview ↗</a>'

        body = f"""<div class="crumbs"><a href="../../index.html">Home</a> /
  <a href="index.html">{esc(project.name)}</a> / {esc(rel_href)}</div>
<section class="page-head">
  <div class="codehead">
    <span class="fname">{esc(rel_href)}</span>
    <span class="tag">{len(lines)} lines</span>
    <span class="tag lang">{esc(LANGUAGE_NAMES.get(full.suffix.lower(), 'file'))}</span>
  </div>
  <div class="btnrow">
    <a class="btn" href="index.html">← Back to {esc(project.name)}</a>
    <a class="btn" href="{repo_url()}/blob/main/{quote(project.name)}/{quote(rel_href)}">View on GitHub ↗</a>
    {preview}
  </div>
</section>
<section>
  <div class="code-wrap">
    <button class="copy" type="button">Copy</button>
    <div class="code-inner">
      <pre class="gutter" aria-hidden="true">{gutter}</pre>
      <pre class="code"><code class="language-{esc(lang)}">{esc(source)}</code></pre>
    </div>
  </div>
</section>"""

        dest = self.out / "labs" / project.slug / (rel_href + ".html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            page(f"{rel_href} · {project.name}", body, depth, self.nav(),
                 description=f"{rel_href} from {project.name}", code_highlight=True,
                 commit=self.commit),
            encoding="utf-8")

    # ---------- misc ----------

    def build_extras(self) -> None:
        (self.out / ".nojekyll").write_text("", encoding="utf-8")
        (self.out / "sitemap.txt").write_text(
            "\n".join([self.site_prefix] +
                      [f"{self.site_prefix}labs/{p.slug}/" for p in self.projects]), encoding="utf-8")
        (self.out / "404.html").write_text(
            page("Not found", """<section class="page-head" style="padding:80px 0">
  <h1>404 — page not found</h1>
  <p>That page is not part of this site. Try the project list instead.</p>
  <div class="btnrow"><a class="btn primary" href="/University-Source-Code/index.html">← Back home</a></div>
</section>""", 0, self.nav(), commit=self.commit),
            encoding="utf-8")

    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.build_home()
        for project in self.projects:
            self.build_project(project)
            for rel in project.rel_files:
                if (project.path / rel).suffix.lower() in CODE_SUFFIXES:
                    self.build_code_page(project, rel)
        self.build_extras()


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the GitHub Pages site.")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--out", default="_site", help="output directory (default: _site)")
    parser.add_argument("--no-readme", action="store_true", help="do not create/update README files")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    builder = SiteBuilder(root, (root / args.out).resolve())

    if not args.no_readme:
        changed: list[str] = []
        # Iterate to a fixed point: writing a README changes the file list it documents
        # (it lists its own line count), so re-scan until a pass makes no changes.
        for _ in range(5):
            wrote_something = False
            builder = SiteBuilder(root, (root / args.out).resolve())
            for project in builder.projects:
                existing = None
                if project.readme.exists():
                    existing = project.readme.read_text(encoding="utf-8", errors="ignore")
                    # only refresh READMEs this script owns; hand-written ones are left alone
                    if not existing.lstrip().startswith(PROJECT_README_MARKER):
                        continue
                generated = generated_project_readme(project, builder.site_prefix)
                if generated != existing:
                    project.readme.write_text(generated, encoding="utf-8")
                    changed.append(project.name)
                    wrote_something = True
            if update_root_readme(root, builder.projects, builder.site_prefix):
                changed.append("README.md")
                wrote_something = True
            if not wrote_something:
                break
        for name in dict.fromkeys(changed):
            print(f"updated README: {name}")

    builder.build()
    print(f"built {len(builder.projects)} project(s) into {builder.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
