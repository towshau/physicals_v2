# Lockeroom Physical Report Generation

Generates stylized, dark-theme PDF reports from HTML/CSS templates.

## Setup

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Scripts

- **`generate_report.py`** — ReportLab-based PDF (Cover, Performance Summary, Physical Results).
- **`generate_html_pdf.py`** — HTML/CSS → PDF via Jinja2 + Playwright (full 11-page report). Output: `Polished_Lockeroom_Report.pdf`.

## Run

```bash
cd reporting
python3 generate_html_pdf.py
```

Output appears in the same directory (or project root if run from there).
