from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import os

class PDFService:
    def __init__(self):
        # Register a font that supports Vietnamese
        # Try to find Arial or Times New Roman in Windows Fonts
        self.font_name = "Helvetica" # Default fallback
        font_path = "C:/Windows/Fonts/Arial.ttf"
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                self.font_name = 'Arial'
        except Exception as e:
            print(f"Could not load font: {e}")

    def create_pdf(self, content: str, output_path: str, title: str = "Meeting Minutes"):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create a custom style with the registered font
        style_body = ParagraphStyle(
            'VietnameseBody',
            parent=styles['BodyText'],
            fontName=self.font_name,
            fontSize=12,
            leading=14,
            spaceAfter=12
        )
        
        style_title = ParagraphStyle(
            'VietnameseTitle',
            parent=styles['Title'],
            fontName=self.font_name,
            fontSize=18,
            spaceAfter=24,
            alignment=1 # Center
        )

        story = []
        
        # Add Title
        story.append(Paragraph(title, style_title))
        story.append(Spacer(1, 12))
        
        # Add Content (handle newlines)
        for line in content.split('\n'):
            if line.strip():
                story.append(Paragraph(line, style_body))
            else:
                story.append(Spacer(1, 12))

        doc.build(story)
        return output_path

