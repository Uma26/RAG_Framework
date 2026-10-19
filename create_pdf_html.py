"""
Convert COMPLETE_GUIDE.md to printable HTML.

This creates an HTML file with professional styling that you can print to PDF.

Usage:
    python create_pdf_html.py

Then:
    1. Open COMPLETE_GUIDE.html in your browser
    2. Press Ctrl+P (or Cmd+P on Mac)
    3. Save as PDF
"""

import re
from pathlib import Path

def create_html_from_markdown():
    """Convert markdown to HTML with styling."""

    # Read markdown
    md_file = Path("COMPLETE_GUIDE.md")
    if not md_file.exists():
        print(f"❌ File not found: {md_file}")
        return False

    print("[*] Reading " + str(md_file) + "...")
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic markdown to HTML conversion
    lines = content.split('\n')
    html_lines = []
    in_code = False
    in_table = False

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                language = line[3:].strip()
                html_lines.append(f'<pre><code class="language-{language}">')
                in_code = True
            continue

        if in_code:
            html_lines.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        # Headers
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{line[5:]}</h4>')
        elif line.startswith('##### '):
            html_lines.append(f'<h5>{line[6:]}</h5>')

        # Horizontal rule
        elif line.startswith('---') or line.startswith('==='):
            html_lines.append('<hr>')

        # Blockquote
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{line[2:]}</blockquote>')

        # Unordered lists
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append(f'<li>{line[2:]}</li>')

        # Empty line
        elif line.strip() == '':
            if html_lines and not html_lines[-1].startswith('<'):
                html_lines.append('</p>')
                html_lines.append('')

        # Regular paragraph
        elif line.strip():
            # Process inline markdown
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)

            if html_lines and html_lines[-1] == '':
                html_lines.append(f'<p>{text}')
            elif html_lines and not html_lines[-1].endswith('</p>'):
                html_lines.append(text)
            else:
                html_lines.append(f'<p>{text}')

    # Create full HTML document
    html_content = '\n'.join(html_lines)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Framework - Complete Guide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            font-size: 16px;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            color: #333;
            background: white;
            padding: 40px 60px;
            max-width: 1100px;
            margin: 0 auto;
        }}

        h1 {{
            color: #1a73e8;
            font-size: 2.8em;
            margin-top: 50px;
            margin-bottom: 20px;
            page-break-after: avoid;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 15px;
        }}

        h1:first-child {{
            margin-top: 0;
        }}

        h2 {{
            color: #1a73e8;
            font-size: 2.2em;
            margin-top: 45px;
            margin-bottom: 18px;
            page-break-after: avoid;
        }}

        h3 {{
            color: #34a853;
            font-size: 1.8em;
            margin-top: 35px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}

        h4 {{
            color: #fbbc04;
            font-size: 1.4em;
            margin-top: 25px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}

        h5 {{
            color: #ea4335;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        p {{
            margin-bottom: 18px;
            text-align: justify;
        }}

        ul, ol {{
            margin-left: 40px;
            margin-bottom: 18px;
        }}

        li {{
            margin-bottom: 10px;
        }}

        code {{
            background-color: #f5f5f5;
            padding: 3px 8px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.95em;
            color: #c7254e;
        }}

        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            border-left: 4px solid #1a73e8;
            padding: 20px;
            margin: 20px 0;
            margin-bottom: 20px;
            overflow-x: auto;
            border-radius: 3px;
            page-break-inside: avoid;
            font-size: 0.9em;
            line-height: 1.5;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            color: #f8f8f2;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            margin-bottom: 20px;
            page-break-inside: avoid;
            border: 1px solid #ddd;
        }}

        th {{
            background-color: #1a73e8;
            color: white;
            padding: 14px;
            text-align: left;
            font-weight: bold;
        }}

        td {{
            border: 1px solid #ddd;
            padding: 12px;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        blockquote {{
            border-left: 5px solid #34a853;
            padding-left: 20px;
            margin-left: 20px;
            margin-bottom: 20px;
            color: #666;
            font-style: italic;
        }}

        a {{
            color: #1a73e8;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 50px 0;
            page-break-after: avoid;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}

        .header h1 {{
            margin-top: 0;
        }}

        .header p {{
            font-size: 1.1em;
            margin-bottom: 10px;
        }}

        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}

        /* Print styles */
        @media print {{
            body {{
                padding: 20px 40px;
            }}

            h1 {{
                page-break-before: always;
            }}

            h1:first-of-type {{
                page-break-before: avoid;
            }}

            h2, h3, h4, h5 {{
                page-break-after: avoid;
            }}

            pre, table {{
                page-break-inside: avoid;
            }}

            ul, ol {{
                page-break-inside: avoid;
            }}

            p {{
                page-break-inside: avoid;
            }}

            a {{
                color: #1a73e8;
            }}
        }}

        /* Dark code syntax highlighting */
        .language-python, .language-bash, .language-json, .language-sql {{
            /* Pre-formatted text */
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RAG Framework - Complete Guide</h1>
        <p><strong>Multi-Tenant Retrieval-Augmented Generation Framework</strong></p>
        <p style="margin-bottom: 30px;">Architecture • Code • Workflows • Model Comparisons • Deployment Guide</p>
    </div>

    {html_content}

    <div class="footer">
        <p>Generated: 2026-07-29</p>
        <p>RAG Framework - Complete Comprehensive Guide</p>
        <p>All code, architecture, workflows, and technology comparisons documented in one place</p>
    </div>
</body>
</html>
"""

    # Save HTML
    html_file = Path("COMPLETE_GUIDE.html")
    print("[*] Saving HTML file...")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    file_size = html_file.stat().st_size / 1024
    print("\n[SUCCESS] HTML file created successfully!")
    print("[FILE] " + str(html_file))
    print("[SIZE] " + str(file_size) + " KB")
    print("\n[INFO] How to convert to PDF:")
    print("   1. Open " + str(html_file) + " in your web browser")
    print("   2. Press Ctrl+P (Windows/Linux) or Cmd+P (Mac)")
    print("   3. Change printer to 'Save as PDF'")
    print("   4. Set margins to 0.5 inches")
    print("   5. Click 'Save' and choose location")
    print("\n[TIP] For best results, use Chrome or Edge browsers")

    return True

if __name__ == "__main__":
    try:
        success = create_html_from_markdown()
        if success:
            print("\n[SUCCESS] Ready to print to PDF!")
    except Exception as e:
        print("[ERROR] " + str(e))
        import traceback
        traceback.print_exc()
