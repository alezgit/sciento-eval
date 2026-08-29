#!/usr/bin/env python3
"""
build.py — Generate ScientoAI evaluation HTML files from .md outputs.

Reads:
  - template.html
  - output_experts/*.md

Outputs (in project root):
  - author1_A.html, author1_B.html, etc. (for GitHub Pages deployment)
  - index.html (neutral portal splash page protecting author privacy)
  - author_links.html (local reference dashboard to copy/test direct links for Google Forms)
"""

import os
import re
import pathlib
from collections import defaultdict

WORKSPACE_DIR = pathlib.Path(__file__).parent.resolve()
TEMPLATE_PATH = WORKSPACE_DIR / "template.html"
MD_DIR        = WORKSPACE_DIR / "output_experts"
PLACEHOLDER   = "{{MARKDOWN_CONTENT}}"


def escape_for_js_template_literal(text: str) -> str:
    """
    Escape backslashes, backticks, and template expressions (${...})
    so the raw markdown can safely reside inside a JS template literal.
    """
    text = text.replace("\\", "\\\\")
    text = text.replace("`", "\\`")
    text = text.replace("${", "\\${")
    return text


def extract_author_name_from_md(md_content: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", md_content, flags=re.MULTILINE)
    if m:
        return re.sub(r"^(Academic\s+)?Narrative\s+CV:\s*", "", m.group(1), flags=re.IGNORECASE).strip()
    return fallback


def generate_neutral_index_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ScientoAI — Expert Evaluation Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bordeaux-main:  #6B0F1A;
      --bordeaux-dark:  #4A0A12;
      --bg-app:         #F8F9FA;
      --text-main:      #1D1D1F;
      --text-muted:     #6E6E73;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: var(--text-main);
      background-color: var(--bg-app);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 24px;
    }
    .portal-card {
      background: #ffffff;
      border-radius: 16px;
      padding: 48px 40px;
      max-width: 580px;
      width: 100%;
      box-shadow: 0 10px 40px rgba(0,0,0,0.08);
      border: 1px solid #EAECEF;
      text-align: center;
    }
    .logo-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(107, 15, 26, 0.08);
      color: var(--bordeaux-main);
      padding: 6px 14px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 0.85rem;
      letter-spacing: 0.5px;
      text-transform: uppercase;
      margin-bottom: 20px;
    }
    h1 {
      font-family: 'Montserrat', sans-serif;
      font-size: 1.7rem;
      font-weight: 800;
      color: var(--bordeaux-main);
      margin-bottom: 14px;
    }
    p {
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 20px;
    }
    .info-box {
      background: #FDF4F5;
      border-left: 4px solid var(--bordeaux-main);
      padding: 14px 18px;
      border-radius: 6px;
      text-align: left;
      font-size: 0.88rem;
      color: #555;
    }
  </style>
</head>
<body>
  <div class="portal-card">
    <div class="logo-badge">⚛ Sciento AI</div>
    <h1>Expert Evaluation Portal</h1>
    <p>This portal hosts individual academic narrative CV evaluation materials.</p>
    <div class="info-box">
      <strong>Direct Link Access Only:</strong> Please use the direct links provided in your official evaluation survey to access assigned candidate documents.
    </div>
  </div>
</body>
</html>
"""


def generate_author_links_html(author_map: dict) -> str:
    rows = []
    for author_id, data in sorted(author_map.items()):
        name = data.get("name", author_id)
        doc_a = data.get("A")
        doc_b = data.get("B")

        a_cell = f'<a href="{doc_a}" target="_blank" class="btn">Open Document A</a>' if doc_a else '<span class="na">N/A</span>'
        b_cell = f'<a href="{doc_b}" target="_blank" class="btn">Open Document B</a>' if doc_b else '<span class="na">N/A</span>'

        rows.append(f"""
        <tr>
          <td>
            <strong>{author_id}</strong>
            <div class="author-name">{name}</div>
          </td>
          <td>{a_cell}</td>
          <td>{b_cell}</td>
        </tr>
        """)

    table_body = "\n".join(rows) if rows else "<tr><td colspan='3'>No outputs found in output_experts/</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ScientoAI Evaluation — Author Links Dashboard (Local)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@700;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bordeaux-main: #6B0F1A;
      --bg-app: #F8F9FA;
    }}
    body {{
      font-family: 'Inter', sans-serif;
      background: var(--bg-app);
      color: #1D1D1F;
      padding: 40px 20px;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
      background: #fff;
      padding: 32px;
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.06);
    }}
    h1 {{
      font-family: 'Montserrat', sans-serif;
      color: var(--bordeaux-main);
      font-size: 1.8rem;
      margin-bottom: 8px;
    }}
    p.sub {{
      color: #6E6E73;
      margin-bottom: 24px;
      font-size: 0.95rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
    }}
    th, td {{
      padding: 14px 16px;
      text-align: left;
      border-bottom: 1px solid #EAECEF;
    }}
    th {{
      background: #FDF4F5;
      color: var(--bordeaux-main);
      font-weight: 700;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .author-name {{
      font-size: 0.85rem;
      color: #6E6E73;
    }}
    .btn {{
      display: inline-block;
      padding: 6px 14px;
      background: var(--bordeaux-main);
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      transition: opacity 0.2s;
    }}
    .btn:hover {{
      opacity: 0.9;
    }}
    .na {{
      color: #aaa;
      font-size: 0.85rem;
    }}
    .hint {{
      margin-top: 24px;
      padding: 12px 16px;
      background: #f0f3f6;
      border-radius: 8px;
      font-size: 0.85rem;
      color: #444;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>ScientoAI Evaluation — Link Directory</h1>
    <p class="sub">Use these links to test pages locally or copy the direct GitHub Pages URLs into your Google Form sections.</p>
    <table>
      <thead>
        <tr>
          <th>Author Identifier</th>
          <th>Section 1 Link (Doc A)</th>
          <th>Section 2 Link (Doc B)</th>
        </tr>
      </thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
    <div class="hint">
      💡 <strong>GitHub Pages Deployment Tip:</strong> Once pushed to your GitHub Pages repository, these links will be located at <code>https://&lt;username&gt;.github.io/&lt;repo&gt;/filename.html</code>.
    </div>
  </div>
</body>
</html>
"""


def build_all():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise ValueError(f"Placeholder '{PLACEHOLDER}' not found in template.html")

    if not MD_DIR.exists():
        print(f"Directory {MD_DIR} does not exist.")
        return

    md_files = sorted(MD_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {MD_DIR}.")
        return

    author_map = defaultdict(dict)
    built_files = []

    print(f"Building evaluation pages from {MD_DIR}...")
    for md_path in md_files:
        md_content = md_path.read_text(encoding="utf-8")
        escaped_content = escape_for_js_template_literal(md_content)
        html_content = template.replace(PLACEHOLDER, escaped_content)

        out_name = f"{md_path.stem}.html"
        out_path = WORKSPACE_DIR / out_name
        out_path.write_text(html_content, encoding="utf-8")
        built_files.append(out_name)
        print(f"  [+] {md_path.name} -> {out_name}")

        # Track for author_links.html
        # E.g. author1_A.md -> author_key = 'author1', variant = 'A'
        stem = md_path.stem
        parts = stem.rsplit("_", 1)
        author_key = parts[0] if len(parts) == 2 else stem
        variant = parts[1] if len(parts) == 2 else "A"

        author_name = extract_author_name_from_md(md_content, fallback=author_key)
        author_map[author_key]["name"] = author_name
        author_map[author_key][variant] = out_name

    # Write neutral index.html
    index_path = WORKSPACE_DIR / "index.html"
    index_path.write_text(generate_neutral_index_html(), encoding="utf-8")
    print("  [+] Generated neutral index.html (Privacy portal)")

    # Write author_links.html
    links_path = WORKSPACE_DIR / "author_links.html"
    links_path.write_text(generate_author_links_html(author_map), encoding="utf-8")
    print("  [+] Generated author_links.html (Helper link directory)")

    print(f"\nSuccessfully generated {len(built_files)} evaluation pages + index.html + author_links.html in {WORKSPACE_DIR}")


if __name__ == "__main__":
    build_all()
