"""
Convert COMPLETE_GUIDE.md to PDF using markdown2 and weasyprint.

Install dependencies:
    pip install markdown2 weasyprint

Run:
    python convert_to_pdf.py
"""

import sys
from pathlib import Path

def create_pdf():
    """Convert markdown to PDF."""

    try:
        # Try importing required libraries
        import markdown2
        from weasyprint import HTML, CSS
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  pip install markdown2 weasyprint")
        return False

    # Read markdown file
    md_file = Path("COMPLETE_GUIDE.md")
    if not md_file.exists():
        print(f"❌ File not found: {md_file}")
        return False

    print(f"📖 Reading {md_file}...")
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    print("🔄 Converting markdown to HTML...")
    html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

    # Create styled HTML
    full_html = f"""
<!DOCTYPE html>
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

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}

        h1 {{
            color: #1a73e8;
            font-size: 2.5em;
            margin-top: 40px;
            margin-bottom: 20px;
            page-break-after: avoid;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 10px;
        }}

        h2 {{
            color: #1a73e8;
            font-size: 2em;
            margin-top: 35px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}

        h3 {{
            color: #34a853;
            font-size: 1.5em;
            margin-top: 25px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        h4 {{
            color: #fbbc04;
            font-size: 1.2em;
            margin-top: 15px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}

        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}

        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        code {{
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }}

        pre {{
            background-color: #f5f5f5;
            border-left: 4px solid #1a73e8;
            padding: 15px;
            margin-bottom: 15px;
            overflow-x: auto;
            border-radius: 3px;
            page-break-inside: avoid;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            font-size: 0.85em;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}

        th {{
            background-color: #1a73e8;
            color: white;
            padding: 12px;
            text-align: left;
        }}

        td {{
            border: 1px solid #ddd;
            padding: 12px;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        tr:hover {{
            background-color: #f0f0f0;
        }}

        blockquote {{
            border-left: 4px solid #34a853;
            padding-left: 15px;
            margin-left: 0;
            margin-bottom: 15px;
            color: #666;
        }}

        a {{
            color: #1a73e8;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .toc {{
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}

        .toc h2 {{
            margin-top: 0;
        }}

        .toc ul {{
            margin-left: 20px;
        }}

        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #fbbc04;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 3px;
        }}

        .success {{
            background-color: #d4edda;
            border-left: 4px solid #34a853;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 3px;
        }}

        .error {{
            background-color: #f8d7da;
            border-left: 4px solid #ea4335;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 3px;
        }}

        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 40px 0;
            page-break-after: avoid;
        }}

        @media print {{
            body {{
                padding: 20px;
            }}

            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}

            pre, table {{
                page-break-inside: avoid;
            }}

            a {{
                color: #1a73e8;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RAG Framework - Complete Guide</h1>
        <p><strong>Multi-Tenant Retrieval-Augmented Generation Framework</strong></p>
        <p>Architecture • Code • Workflows • Model Comparisons • Deployment Guide</p>
        <hr>
    </div>

    {html_content}

    <hr>
    <div class="footer" style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated: 2026-07-29</p>
        <p>RAG Framework Documentation</p>
    </div>
</body>
</html>
"""

    # Save HTML
    html_file = Path("COMPLETE_GUIDE.html")
    print(f"💾 Saving HTML to {html_file}...")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    # Convert HTML to PDF
    try:
        print("📄 Converting HTML to PDF (this may take a minute)...")
        pdf_file = Path("COMPLETE_GUIDE.pdf")
        HTML(string=full_html).write_pdf(pdf_file)
        print(f"✅ PDF created successfully: {pdf_file}")
        print(f"   Size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ PDF conversion failed: {e}")
        print(f"\n✓ HTML file created at: {html_file}")
        print("  You can open this in a browser and print to PDF (Ctrl+P)")
        return False

if __name__ == "__main__":
    success = create_pdf()
    sys.exit(0 if success else 1)
