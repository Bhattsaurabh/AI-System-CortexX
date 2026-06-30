from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def draw_slide(c, title, points, page_num):
    # Background
    c.setFillColor(colors.HexColor("#0f172a")) # Slate 900
    c.rect(0, 0, 792, 612, fill=True, stroke=False)
    
    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(50, 520, title)
    
    # Divider
    c.setStrokeColor(colors.HexColor("#3b82f6")) # Blue 500
    c.setLineWidth(2)
    c.line(50, 500, 742, 500)
    
    # Points
    c.setFont("Helvetica", 24)
    c.setFillColor(colors.HexColor("#e2e8f0")) # Slate 200
    y = 440
    for point in points:
        c.drawString(70, y, f"• {point}")
        y -= 40
        
    # Page Number
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.gray)
    c.drawString(750, 30, str(page_num))
    c.showPage()

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    
    # Slide 1: Title
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, 0, 792, 612, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 54)
    c.drawCentredString(396, 340, "CortexX AI System")
    c.setFont("Helvetica", 28)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawCentredString(396, 280, "An AI-Native Autonomous Engineering System")
    c.drawCentredString(396, 240, "Built with Next.js & FastAPI")
    c.showPage()
    
    # Slide 2: Overview
    draw_slide(c, "Project Overview", [
        "CortexX is a next-generation Multi-Agent AI system.",
        "Frontend: Stunning Next.js Glassmorphism UI.",
        "Backend: High-performance Python FastAPI server.",
        "LLMs: Powered by Google's Gemini advanced models.",
        "Two core modes: General Chat Copilot and Project Builder."
    ], 2)
    
    # Slide 3: General Chat
    draw_slide(c, "General Chat Copilot", [
        "Intelligent routing to specialized AI sub-agents.",
        "Code Intel Agent: Analyzes architecture & refactors code.",
        "Debug Agent: Rapid log parsing & root-cause identification.",
        "DevOps Agent: CI/CD pipeline monitoring & troubleshooting.",
        "Knowledge Agent: Semantic search across the codebase."
    ], 3)
    
    # Slide 4: Builder
    draw_slide(c, "Autonomous Project Builder", [
        "Gives the AI physical agency over your local machine.",
        "Provides absolute workspace paths for code generation.",
        "LangChain ReAct loop executes tasks iteratively.",
        "Tool integrations: Read files, perform surgical edits.",
        "Executes terminal commands to install & run apps."
    ], 4)
    
    # Slide 5: Conclusion
    draw_slide(c, "Conclusion", [
        "Bridges the gap between passive chat and active engineering.",
        "Acts as an autonomous digital teammate, not just a generator.",
        "Secure local deployment with Cloudflare tunneling.",
        "Fully capable of building & maintaining complex systems.",
        "Revolutionizing how developers interact with codebases."
    ], 5)
    
    c.save()

if __name__ == "__main__":
    create_pdf("CortexX_Presentation.pdf")
    print("Successfully generated CortexX_Presentation.pdf")
