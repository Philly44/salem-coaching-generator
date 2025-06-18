import streamlit as st
import anthropic
import os
from datetime import datetime
from io import BytesIO

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, gray, HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# Page configuration
st.set_page_config(
    page_title="Salem University Coaching Guide Generator",
    page_icon="📊",
    layout="wide"
)

class SalemCoachingGenerator:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key, max_retries=3)
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        # Header style - EXACT SALEM UNIVERSITY STYLING
        self.header_style = ParagraphStyle(
            'SalemHeader',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=HexColor('#1f4e79'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=0
        )
        
        # Title style
        self.title_style = ParagraphStyle(
            'SalemTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=black,
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=4
        )
        
        # Date style
        self.date_style = ParagraphStyle(
            'SalemDate',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=gray,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            spaceAfter=20
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=HexColor('#1f4e79'),
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=20,
            borderWidth=1,
            borderColor=HexColor('#1f4e79'),
            borderPadding=8,
            backColor=HexColor('#f0f4f8')
        )
        
        # Performance level style
        self.performance_style = ParagraphStyle(
            'Performance',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=8
        )
        
        # Quote style
        self.quote_style = ParagraphStyle(
            'Quote',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            fontName='Helvetica-Oblique',
            spaceAfter=6,
            textColor=HexColor('#333333')
        )
        
        # Focus area style
        self.focus_style = ParagraphStyle(
            'Focus',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            spaceAfter=4,
            leftIndent=10
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )

def call_claude_with_prompt(self, prompt_content, transcript):
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user", 
                        "content": f"{prompt_content}\n\nTranscript to analyze:\n{transcript}"
                    }
                ]
            )
            return message.content[0].text
            
        except Exception as e:
            return f"Error calling Claude API: {str(e)}"
            
    def load_prompt_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: Could not find prompt file {filename}"
        except Exception as e:
            return f"Error reading file {filename}: {str(e)}"

    def generate_complete_guide(self, transcript):
        results = {}
        
        prompt_files = {
            'header': '01_title_prompt.txt',
            'great_moment': '02_most_impactful_statement_prompt.txt',
            'scorecard': '04_interview_scorecard_prompt.txt',
            'talk_ratio': '09_talk_time_prompt.txt',
            'invitation': '05_application_invitation_assessment_prompt.txt',
            'growth_plan': '06_weekly_growth_plan_prompt.txt',
            'coaching_notes': '07_coaching_notes_prompt.txt'
        }
        
        for section, filename in prompt_files.items():
            prompt_content = self.load_prompt_file(filename)
            if not prompt_content.startswith("Error:"):
                results[section] = self.call_claude_with_prompt(prompt_content, transcript)
            else:
                results[section] = prompt_content
                
        return results

    def parse_scorecard_table(self, scorecard_text):
        lines = scorecard_text.split('\n')
        table_data = []
        
        for line in lines:
            if '|' in line and not line.strip().startswith('|---'):
                cells = [cell.strip() for cell in line.split('|')]
                if len(cells) >= 4:
                    clean_cells = [cell for cell in cells if cell]
                    if len(clean_cells) >= 4:
                        table_data.append(clean_cells[:4])
        
        return table_data

    def parse_talk_ratio_table(self, talk_ratio_text):
        lines = talk_ratio_text.split('\n')
        table_data = []
        
        for line in lines:
            if '|' in line and not line.strip().startswith('|---'):
                cells = [cell.strip() for cell in line.split('|')]
                clean_cells = [cell for cell in cells if cell]
                if len(clean_cells) >= 3:
                    table_data.append(clean_cells[:3])
        
        return table_data

    def parse_invitation_table(self, invitation_text):
        lines = invitation_text.split('\n')
        table_data = []
        
        for line in lines:
            if '|' in line and not line.strip().startswith('|---'):
                cells = [cell.strip() for cell in line.split('|')]
                clean_cells = [cell for cell in cells if cell]
                if len(clean_cells) >= 3:
                    table_data.append(clean_cells[:3])
        
        return table_data

    def extract_section_details(self, scorecard_text):
        sections = []
        current_section = None
        
        lines = scorecard_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('### SECTION'):
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'title': line.replace('### ', ''),
                    'performance': '',
                    'quote': '',
                    'focus': ''
                }
            elif current_section:
                if line.startswith('**') and not '"' in line and not 'Focus Area' in line:
                    current_section['performance'] = line
                elif '"' in line and '(' in line:
                    current_section['quote'] = line
                elif line.startswith('**Focus Area:**'):
                    current_section['focus'] = line
        
        if current_section:
            sections.append(current_section)
            
        return sections

    def create_pdf(self, results):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        story = []
        
        # 1. HEADER SECTION - EXACT SALEM STYLING
        story.append(Paragraph("SALEM UNIVERSITY", self.header_style))
        story.append(Paragraph("Coaching Development Report", self.title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.date_style))
        
        story.append(Spacer(1, 12))
        
        # 2. PERFORMANCE SCORECARD - PROFESSIONAL TABLES
        story.append(Paragraph("Performance Scorecard", self.section_style))
        
        if 'scorecard' in results:
            table_data = self.parse_scorecard_table(results['scorecard'])
            
            if table_data:
                table = Table(table_data, colWidths=[0.8*inch, 2.8*inch, 1.8*inch, 2.2*inch])
                table.setStyle(TableStyle([
                    # Header row styling - SALEM BLUE
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9fa'), HexColor('#ffffff')])
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Add detailed sections
            sections = self.extract_section_details(results['scorecard'])
            for section in sections:
                story.append(Paragraph(section['title'], self.performance_style))
                if section['performance']:
                    story.append(Paragraph(section['performance'], self.performance_style))
                if section['quote']:
                    story.append(Paragraph(section['quote'], self.quote_style))
                if section['focus']:
                    story.append(Paragraph(section['focus'], self.focus_style))
                story.append(Spacer(1, 12))
        
        # 3. COMMUNICATION ANALYSIS
        story.append(Paragraph("Communication Analysis", self.section_style))
        
        if 'talk_ratio' in results:
            table_data = self.parse_talk_ratio_table(results['talk_ratio'])
            if table_data:
                table = Table(table_data, colWidths=[2.2*inch, 2.2*inch, 2.2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                story.append(table)
                story.append(Spacer(1, 20))
        
        # 4. DEVELOPMENT GROWTH PLAN
        if 'growth_plan' in results:
            story.append(Paragraph("Development Growth Plan", self.section_style))
            
            lines = results['growth_plan'].split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('## Weekly Growth Plan'):
                    continue
                elif line.startswith('**Strategy'):
                    story.append(Paragraph(line, self.performance_style))
                elif line.startswith('- **Key Phrases:**') or line.startswith('- **When to Use:**'):
                    story.append(Paragraph(line, self.focus_style))
                elif line.strip().startswith('- "'):
                    story.append(Paragraph(line, self.quote_style))
                elif line and not line.startswith('#'):
                    story.append(Paragraph(line, self.body_style))
            
            story.append(Spacer(1, 20))
        
        # 5. COACHING SESSION NOTES
        if 'coaching_notes' in results:
            story.append(Paragraph("Coaching Session Notes", self.section_style))
            
            lines = results['coaching_notes'].split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    story.append(Paragraph(line, self.body_style))
            
            story.append(Spacer(1, 20))
        
        # 6. APPLICATION INVITATION ASSESSMENT
        if 'invitation' in results:
            story.append(Paragraph("Application Invitation Assessment", self.section_style))
            
            table_data = self.parse_invitation_table(results['invitation'])
            if table_data:
                table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ffffff')),
                    ('GRID', (0, 0), (-1, -1), 1, black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(table)
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data


def main():
    st.title("📊 Salem University Coaching Guide Generator")
    st.markdown("Transform conversation transcripts into professional coaching reports using AI analysis.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("📝 Transcript Input")
        
        transcript = st.text_area(
            "Paste your conversation transcript here:",
            height=400,
            placeholder="Paste your conversation transcript here...\n\nExample:\nJW\nJon Wagner\n00:01\nHello, this is Jon from Salem University..."
        )
    
    with col2:
        st.header("⚙️ Generate Report")
        
        api_key = st.text_input(
            "Claude API Key:",
            type="password",
            help="Enter your Anthropic Claude API key"
        )
        
        generate_button = st.button(
            "🚀 Generate Coaching Guide",
            type="primary",
            disabled=not (transcript and api_key)
        )
    
    if generate_button and transcript and api_key:
        try:
            with st.spinner("Generating coaching guide..."):
                
                generator = SalemCoachingGenerator(api_key)
                
                st.info("📋 Analyzing transcript with Claude AI...")
                results = generator.generate_complete_guide(transcript)
                
                st.info("📄 Creating professional PDF report...")
                pdf_data = generator.create_pdf(results)
                
                st.success("✅ Coaching guide generated successfully!")
                
                st.download_button(
                    label="📥 Download Salem University Coaching Guide",
                    data=pdf_data,
                    file_name=f"salem_coaching_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
                
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")

if __name__ == "__main__":
    main()
