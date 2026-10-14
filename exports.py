import csv
import io
import os
import tempfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

def make_csv(rows):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    fields = ["name", "state", "city", "type", "rating", "entrance_fee", "visit_hours", "best_time"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path

def make_pdf(plan):
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("Explore India — Trip Plan", styles["Title"]), Spacer(1, 8)]
    story.append(Paragraph(f"Budget: INR {plan['budget']:,.0f} | Available time: {plan['hours_available']} hours", styles["Normal"]))
    story.append(Paragraph(f"Entrance fees: INR {plan['total_fee']:,.0f} | Planned visit time: {plan['total_hours']} hours", styles["Normal"]))
    story.append(Spacer(1, 12))
    data = [["Attraction", "Location", "Rating", "Fee (INR)", "Hours"]]
    for item in plan["items"]:
        data.append([item.get("name",""), f"{item.get('city','')}, {item.get('state','')}",
                     str(item.get("rating","")), f"{item.get('entrance_fee',0):.0f}", str(item.get("visit_hours",""))])
    table = Table(data, repeatRows=1, colWidths=[48*mm, 48*mm, 18*mm, 22*mm, 18*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#183B56")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D8E1E8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F3F7FA")]),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("PADDING", (0,0), (-1,-1), 6)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Note: This estimate includes dataset entrance fees only. Travel, food and accommodation are excluded.", styles["Italic"]))
    doc.build(story)
    return path
