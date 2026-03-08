from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

def draw_background(c, width, height):
    """Fills the background with a dark, off-black color."""
    c.setFillColorRGB(0.05, 0.05, 0.05) # Very dark grey/black
    c.rect(0, 0, width, height, stroke=0, fill=1)

def create_cover_page(c, width, height, data):
    draw_background(c, width, height)
    
    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(inch, height - 3*inch, "Your Physical™ Report")
    
    # Client Info
    c.setFont("Helvetica", 18)
    c.setFillColorRGB(0.7, 0.7, 0.7) # Light grey
    c.drawString(inch, height - 3.5*inch, f"Client: {data['name']}")
    
    c.setFont("Helvetica", 12)
    c.drawString(inch, height - 4*inch, f"DOB: {data['dob']}")
    c.drawString(inch, height - 4.3*inch, f"Assessor: {data['assessor']}")
    c.drawString(inch, height - 4.6*inch, f"Date: {data['date']}")
    
    # Footer
    c.setFillColorRGB(0.8, 0.4, 0.0) # Accent orange
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, inch, "LOCKEROOM")
    c.showPage()

def create_summary_page(c, width, height, data):
    draw_background(c, width, height)
    
    # Header
    c.setFillColorRGB(0.8, 0.4, 0.0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, height - inch, "LOCKEROOM")
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(inch, height - 1.5*inch, "Your Performance Summary")
    
    # Draw Metric Boxes
    box_y = height - 4*inch
    box_width = 1.8 * inch
    box_height = 2 * inch
    spacing = 2 * inch
    
    metrics = [
        ("Health", data['health_score'], data['health_stage']),
        ("Fitness", data['fitness_score'], data['fitness_stage']),
        ("Strength", data['strength_score'], data['strength_stage'])
    ]
    
    for i, (title, score, stage) in enumerate(metrics):
        box_x = inch + (i * spacing)
        
        # Draw Box
        c.setStrokeColorRGB(0.3, 0.3, 0.3)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.rect(box_x, box_y, box_width, box_height, stroke=1, fill=1)
        
        # Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 14)
        c.drawCentredString(box_x + box_width/2, box_y + box_height - 0.5*inch, title)
        
        # Score
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(box_x + box_width/2, box_y + box_height - 1.2*inch, score)
        
        # Stage Indicator
        c.setFillColorRGB(0.8, 0.4, 0.0) # Orange accent for stage
        c.setFont("Helvetica", 12)
        c.drawCentredString(box_x + box_width/2, box_y + 0.3*inch, stage)

    # Footer note
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.setFont("Helvetica", 10)
    c.drawString(inch, inch, "Your performance summary combines multiple tests in each category.")
    
    c.showPage()

def create_detailed_results_page(c, width, height, data):
    draw_background(c, width, height)
    
    # Header
    c.setFillColorRGB(0.8, 0.4, 0.0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, height - inch, "LOCKEROOM")
    
    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(inch, height - 1.5*inch, "Physical Results")
    
    # Table layout: two columns (Metric, Value)
    table_top = height - 2.5*inch
    col1_width = 2.5 * inch
    col2_width = 2.0 * inch
    row_height = 0.45 * inch
    header_bg = (0.2, 0.2, 0.2)
    row_bg = (0.12, 0.12, 0.12)
    border_grey = (0.3, 0.3, 0.3)
    left = inch
    
    rows = [
        ("Metric", "Value"),
        ("Body Fat %", data["body_fat"]),
        ("VO2 Max", data["vo2_max"]),
        ("Push Up Score", data["push_up_score"]),
        ("Vertical Jump", data["vertical_jump"]),
    ]
    
    for i, (metric, value) in enumerate(rows):
        y = table_top - i * row_height
        is_header = i == 0
        bg = header_bg if is_header else row_bg
        c.setFillColorRGB(*bg)
        c.setStrokeColorRGB(*border_grey)
        c.rect(left, y - row_height, col1_width, row_height, stroke=1, fill=1)
        c.rect(left + col1_width, y - row_height, col2_width, row_height, stroke=1, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold" if is_header else "Helvetica", 11)
        c.drawString(left + 0.15*inch, y - row_height + 0.14*inch, metric)
        c.drawString(left + col1_width + 0.15*inch, y - row_height + 0.14*inch, str(value))
    
    c.showPage()

def generate_pdf(filename):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Dummy Data based on Kathy Xu's report
    dummy_data = {
        "name": "Kathy Xu",
        "dob": "20.07.1989",
        "assessor": "James Deacy",
        "date": "03.03.2026",
        "health_score": "6.4 / 10",
        "health_stage": "Stage 2",
        "fitness_score": "7.0 / 10",
        "fitness_stage": "Stage 2",
        "strength_score": "6.5 / 10",
        "strength_stage": "Stage 2",
        "body_fat": "22.6",
        "vo2_max": "32",
        "push_up_score": "5.9/10",
        "vertical_jump": "6.9/10"
    }
    
    create_cover_page(c, width, height, dummy_data)
    create_summary_page(c, width, height, dummy_data)
    create_detailed_results_page(c, width, height, dummy_data)
    
    c.save()
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    generate_pdf("Sample_Lockeroom_Report.pdf")
