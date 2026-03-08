"""
Generate a polished multi-page PDF from an HTML/CSS template
using Jinja2 for templating and Playwright for rendering.
"""
import asyncio
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright


def get_dummy_data() -> dict:
    """Comprehensive dummy data based on Kathy Xu's Lockeroom Physical report."""
    return {
        "name": "Kathy Xu",
        "dob": "20. 07. 1989",
        "assessor": "James Deacy",
        "date": "03. 03. 2026",
        "next_physical": "4-6 Months",
        "category": "Female, Ages 40 & Under",
        "total_pages": 11,

        # Performance Summary (page 4)
        "health_score": "6.4",
        "health_stage": 2,
        "fitness_score": "7.0",
        "fitness_stage": 2,
        "strength_score": "6.5",
        "strength_stage": 2,

        # Health details (page 5)
        "body_fat": "22.6",
        "inbody_points": "74",

        # Fitness details (page 6)
        "vo2_max": "32",
        "vo2_stage": 2,
        "vo2_ranges": {
            "s1": "F < 27",
            "s2": "F 28-35",
            "s3": "F 36-44",
            "s4": "F 45+",
        },

        # Strength details (page 7)
        "push_up_score": "5.9",
        "push_up_stage": 1,
        "vertical_jump_score": "6.9",
        "vertical_jump_stage": 2,
        "chin_hold_score": "6.7",
        "chin_hold_stage": 2,

        # Bonus metrics (page 8)
        "rsi_score": "5.5",
        "rsi_stage": 1,
        "agility_score": "N/A",

        # Journey stages (page 2)
        "stages": [
            {
                "num": 1,
                "name": "Reset",
                "range": "0/10 – 5.9/10",
                "description": (
                    "This is your starting point, all uphill from here. "
                    "Now we get to work, focusing on helping you feel better, "
                    "move better, and build momentum to improve this score."
                ),
            },
            {
                "num": 2,
                "name": "Baseline",
                "range": "6/10 – 7.9/10",
                "description": (
                    "A common place to be. You've laid some foundations, "
                    "and now the focus is steady progress and doing the "
                    "basics right."
                ),
            },
            {
                "num": 3,
                "name": "Longevity",
                "range": "8/10 – 9.9/10",
                "description": (
                    "You're building lasting strength and protecting your "
                    "health long-term. Everything here supports living well "
                    "for longer with energy, resilience, and freedom."
                ),
            },
            {
                "num": 4,
                "name": "Performance",
                "range": "10+",
                "description": (
                    "You've done the work, now it's about exploring your "
                    "potential. This stage is for sharpening performance, "
                    "chasing goals, and pushing personal bests."
                ),
            },
        ],

        # Physical Results table (page 3)
        "result_groups": [
            {
                "pillar": "Health",
                "tests": [
                    {
                        "name": "Body Fat %",
                        "result": "22.6",
                        "active": 3,
                        "s1": "M 30%+\nF 38%+",
                        "s2": "M 29-20%\nF 37-28%",
                        "s3": "M 19-13%\nF 27-20%",
                        "s4": "M 12-8%\nF 19-14%",
                    },
                    {
                        "name": "InBody Points",
                        "result": "74",
                        "active": 2,
                        "s1": "< 69",
                        "s2": "70-79",
                        "s3": "80-89",
                        "s4": "90+",
                    },
                ],
            },
            {
                "pillar": "Fitness",
                "tests": [
                    {
                        "name": "VO2 Max",
                        "result": "32.11",
                        "active": 2,
                        "s1": "M < 30\nF < 27",
                        "s2": "M 31-44\nF 28-35",
                        "s3": "M 45-54\nF 36-44",
                        "s4": "M 55+\nF 45+",
                    },
                    {
                        "name": "1 Mile Run",
                        "result": "N/A",
                        "active": 0,
                        "s1": "M > 9:01\nF > 10:00",
                        "s2": "M < 9:00\nF < 9:59",
                        "s3": "M < 7:30\nF < 8:30",
                        "s4": "M < 6:00\nF < 7:00",
                    },
                ],
            },
            {
                "pillar": "Strength (Lean Muscle)",
                "tests": [
                    {
                        "name": "Military Push Up (Tempo)",
                        "result": "5",
                        "active": 2,
                        "s1": "M < 15\nF < 5",
                        "s2": "M 16-30\nF 5-10",
                        "s3": "M 30-49\nF 11-30",
                        "s4": "M 50+\nF 31+",
                    },
                    {
                        "name": "Max Length Chin Hold",
                        "result": "34",
                        "active": 2,
                        "s1": "< 20s",
                        "s2": "20s-59s",
                        "s3": "60-89s",
                        "s4": "90s+",
                    },
                    {
                        "name": "Max Grip Strength",
                        "result": "30",
                        "active": 2,
                        "s1": "M < 40kg\nF < 25kg",
                        "s2": "M 40-49kg\nF 25-30kg",
                        "s3": "M 50-60kg\nF 30-40kg",
                        "s4": "M 61kg+\nF 41kg+",
                    },
                ],
            },
            {
                "pillar": "Strength (Power & Agility)",
                "tests": [
                    {
                        "name": "4 Jump RSI",
                        "result": "1.48",
                        "active": 1,
                        "s1": "M < 2.0\nF < 1.5",
                        "s2": "M 2.0-2.5\nF 1.5-2.0",
                        "s3": "M 2.5-3.0\nF 2.0-2.5",
                        "s4": "M 3.0+\nF 2.51+",
                    },
                    {
                        "name": "Cross Over Hop",
                        "result": "N/A",
                        "active": 0,
                        "s1": "< 45",
                        "s2": "46-65",
                        "s3": "66-80",
                        "s4": "81+",
                    },
                    {
                        "name": "Max Vertical Jump",
                        "result": "27",
                        "active": 2,
                        "s1": "M < 35cm\nF < 25cm",
                        "s2": "M 35-45cm\nF 25-35cm",
                        "s3": "M 46-49cm\nF 35-44cm",
                        "s4": "M 60cm+\nF 45cm+",
                    },
                    {
                        "name": "Single Leg RSI",
                        "result": "N/A",
                        "active": 0,
                        "s1": "M < 0.75\nF < 0.5",
                        "s2": "M 0.75-1.25\nF 0.5-0.8",
                        "s3": "M 1.26-1.75\nF 1.2-1.5",
                        "s4": "M 1.76+\nF 1.6+",
                    },
                ],
            },
        ],
    }


def render_html(data: dict) -> str:
    template_dir = Path(__file__).resolve().parent
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("template.html")
    return template.render(**data)


async def html_to_pdf(html: str, output_path: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path=output_path,
            print_background=True,
            format="A4",
        )
        await browser.close()


def generate_pdf(filename: str = "Polished_Lockeroom_Report.pdf") -> None:
    data = get_dummy_data()
    html = render_html(data)
    output_path = Path(__file__).resolve().parent / filename
    asyncio.run(html_to_pdf(html, str(output_path)))
    print(f"PDF generated successfully: {output_path}")


if __name__ == "__main__":
    generate_pdf()
