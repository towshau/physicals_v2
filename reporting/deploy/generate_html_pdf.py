"""
Generate a polished multi-page PDF from an HTML/CSS template
using Jinja2 for templating and Playwright (Chromium) for rendering.
"""
import asyncio
import base64
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR / "assets"


def _b64_img(filename: str) -> str:
    """Return a data-URI for an image file in assets/."""
    path = ASSETS_DIR / filename
    encoded = base64.b64encode(path.read_bytes()).decode()
    suffix = path.suffix.lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(suffix, "image/png")
    return f"data:{mime};base64,{encoded}"


def get_dummy_data() -> dict:
    today = date.today().strftime("%d. %m. %Y")
    return {
        "name": "Kathy Xu",
        "dob": "20. 07. 1989",
        "assessor": "James Deacy",
        "date": "03. 03. 2026",
        "report_date": today,
        "category": "Female, Ages 40 & Under",
        "total_pages": 3,

        "logo_b64": _b64_img("logo.png"),
        "hero_b64": _b64_img("hero.png"),

        "stages": [
            {"num": 1, "name": "Reset", "range": "0/10 – 5.9/10",
             "description": "This is your starting point, all uphill from here. Now we get to work, focusing on helping you feel better, move better, and build momentum."},
            {"num": 2, "name": "Baseline", "range": "6/10 – 7.9/10",
             "description": "A common place to be. You've laid some foundations, and now the focus is steady progress and doing the basics right."},
            {"num": 3, "name": "Longevity", "range": "8/10 – 9.9/10",
             "description": "You're building lasting strength and protecting your health long-term. Everything here supports living well for longer with energy and resilience."},
            {"num": 4, "name": "Performance", "range": "10+",
             "description": "You've done the work, now it's about exploring your potential. This stage is for sharpening performance and pushing personal bests."},
        ],

        "result_groups": [
            {"pillar": "Health", "tests": [
                {"name": "Body Fat %",
                 "first_value": "24.1", "first_date": "12 Jan 2024", "first_stage": 2,
                 "second_value": "23.2", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "22.6", "most_recent_date": "10 Mar 2026", "most_recent_stage": 3,
                 "s1": "M 30%+\nF 38%+", "s2": "M 29-20%\nF 37-28%", "s3": "M 19-13%\nF 27-20%", "s4": "M 12-8%\nF 19-14%"},
                {"name": "Body Weight",
                 "first_value": "62.5", "first_date": "12 Jan 2024", "first_stage": 0,
                 "second_value": "61.8", "second_date": "15 Jun 2025", "second_stage": 0,
                 "most_recent_value": "60.9", "most_recent_date": "10 Mar 2026", "most_recent_stage": 0,
                 "s1": "", "s2": "", "s3": "", "s4": ""},
                {"name": "InBody Points",
                 "first_value": "70", "first_date": "12 Jan 2024", "first_stage": 2,
                 "second_value": "72", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "74", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "< 69", "s2": "70-79", "s3": "80-89", "s4": "90+"},
            ]},
            {"pillar": "Fitness", "tests": [
                {"name": "VO2 Max",
                 "first_value": "28.5", "first_date": "12 Jan 2024", "first_stage": 1,
                 "second_value": "30.2", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "32.11", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "M < 30\nF < 27", "s2": "M 31-44\nF 28-35", "s3": "M 45-54\nF 36-44", "s4": "M 55+\nF 45+"},
                {"name": "1 Mile Run",
                 "first_value": "N/A", "first_date": "—", "first_stage": 0,
                 "second_value": "N/A", "second_date": "—", "second_stage": 0,
                 "most_recent_value": "N/A", "most_recent_date": "—", "most_recent_stage": 0,
                 "s1": "M > 9:01\nF > 10:00", "s2": "M < 9:00\nF < 9:59", "s3": "M < 7:30\nF < 8:30", "s4": "M < 6:00\nF < 7:00"},
            ]},
            {"pillar": "Strength (Lean)", "tests": [
                {"name": "Military Push Up (Tempo)",
                 "first_value": "4", "first_date": "12 Jan 2024", "first_stage": 1,
                 "second_value": "5", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "5", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "M < 15\nF < 5", "s2": "M 16-30\nF 5-10", "s3": "M 30-49\nF 11-30", "s4": "M 50+\nF 31+"},
                {"name": "Max Length Chin Hold",
                 "first_value": "28", "first_date": "12 Jan 2024", "first_stage": 2,
                 "second_value": "32", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "34", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "< 20s", "s2": "20s-59s", "s3": "60-89s", "s4": "90s+"},
                {"name": "Max Grip Strength",
                 "first_value": "26", "first_date": "12 Jan 2024", "first_stage": 1,
                 "second_value": "28", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "30", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "M < 40kg\nF < 25kg", "s2": "M 40-49kg\nF 25-30kg", "s3": "M 50-60kg\nF 30-40kg", "s4": "M 61kg+\nF 41kg+"},
            ]},
            {"pillar": "Strength (Power)", "tests": [
                {"name": "4 Jump RSI",
                 "first_value": "1.32", "first_date": "12 Jan 2024", "first_stage": 1,
                 "second_value": "1.40", "second_date": "15 Jun 2025", "second_stage": 1,
                 "most_recent_value": "1.48", "most_recent_date": "10 Mar 2026", "most_recent_stage": 1,
                 "s1": "M < 2.0\nF < 1.5", "s2": "M 2.0-2.5\nF 1.5-2.0", "s3": "M 2.5-3.0\nF 2.0-2.5", "s4": "M 3.0+\nF 2.51+"},
                {"name": "Cross Over Hop",
                 "first_value": "N/A", "first_date": "—", "first_stage": 0,
                 "second_value": "N/A", "second_date": "—", "second_stage": 0,
                 "most_recent_value": "N/A", "most_recent_date": "7 Dec 2024", "most_recent_stage": 0,
                 "s1": "< 45", "s2": "46-65", "s3": "66-80", "s4": "81+"},
                {"name": "Max Vertical Jump",
                 "first_value": "24", "first_date": "12 Jan 2024", "first_stage": 1,
                 "second_value": "26", "second_date": "15 Jun 2025", "second_stage": 2,
                 "most_recent_value": "27", "most_recent_date": "10 Mar 2026", "most_recent_stage": 2,
                 "s1": "M < 35cm\nF < 25cm", "s2": "M 35-45cm\nF 25-35cm", "s3": "M 46-49cm\nF 35-44cm", "s4": "M 60cm+\nF 45cm+"},
            ]},
        ],
    }


def render_html(data: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(SCRIPT_DIR)))
    template = env.get_template("template.html")
    return template.render(**data)


async def _html_to_pdf_bytes(html: str) -> bytes:
    """Render HTML to PDF and return raw bytes (no file written)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1123, "height": 794},
            device_scale_factor=2,
        )
        await page.set_content(html, wait_until="networkidle")
        pdf_bytes = await page.pdf(
            print_background=True,
            format="A4",
            landscape=True,
            prefer_css_page_size=True,
        )
        await browser.close()
    return pdf_bytes


def generate_pdf_bytes(data: dict) -> bytes:
    """Accept a report-payload dict, inject assets, and return PDF bytes."""
    data.setdefault("logo_b64", _b64_img("logo.png"))
    data.setdefault("hero_b64", _b64_img("hero.png"))
    data.setdefault("total_pages", 3)
    data.setdefault("stages", [
        {"num": 1, "name": "Reset", "range": "0/10 – 5.9/10",
         "description": "This is your starting point, all uphill from here. Now we get to work, focusing on helping you feel better, move better, and build momentum."},
        {"num": 2, "name": "Baseline", "range": "6/10 – 7.9/10",
         "description": "A common place to be. You've laid some foundations, and now the focus is steady progress and doing the basics right."},
        {"num": 3, "name": "Longevity", "range": "8/10 – 9.9/10",
         "description": "You're building lasting strength and protecting your health long-term. Everything here supports living well for longer with energy and resilience."},
        {"num": 4, "name": "Performance", "range": "10+",
         "description": "You've done the work, now it's about exploring your potential. This stage is for sharpening performance and pushing personal bests."},
    ])
    html = render_html(data)
    return asyncio.run(_html_to_pdf_bytes(html))


def generate_pdf(filename: str | None = None) -> None:
    """CLI helper: generate PDF from dummy data and write to disk."""
    data = get_dummy_data()
    if filename is None:
        safe_name = data["name"].replace(" ", "_")
        today_str = date.today().strftime("%Y-%m-%d")
        filename = f"{safe_name}_Physical_Report_{today_str}.pdf"
    pdf_bytes = generate_pdf_bytes(data)
    output_path = SCRIPT_DIR / filename
    output_path.write_bytes(pdf_bytes)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    generate_pdf()
