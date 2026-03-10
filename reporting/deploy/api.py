"""
FastAPI wrapper around the PDF report generator.
POST /generate-report with the report payload JSON → returns PDF bytes.
"""
from fastapi import FastAPI, Request
from fastapi.responses import Response

from generate_html_pdf import async_generate_pdf_bytes

app = FastAPI(title="Lockeroom Physical Report API")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate-report")
async def generate_report(request: Request):
    data = await request.json()
    pdf_bytes = await async_generate_pdf_bytes(data)
    safe_name = data.get("name", "Report").replace(" ", "_")
    filename = f"{safe_name}_Physical_Report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
