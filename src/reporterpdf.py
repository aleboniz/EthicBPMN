from fpdf import FPDF
from datetime import datetime

class PDFReportGenerator:
    @staticmethod
    def generate_pdf(violations, ai_feedback, metrics, nodes, output_path="report_audit.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        def clean(text):
            if text is None:
                return "N/A"
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 15, "EthicBPMN Audit Report", ln=True, align='C')
        
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 5, f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean("1. Valutazione Sintetica"), ln=True)
        pdf.set_fill_color(245, 245, 245)
        
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"  - Ethical Risk Index (ERI): {metrics.get('eri', '0')}", ln=True, fill=True)
        pdf.cell(0, 8, f"  - Observed Risk (R_obs): {metrics.get('r_obs', '0')}", ln=True, fill=True)
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"  -> Punteggio Finale EPS: {metrics.get('eps', '0')} / 1.00", ln=True, fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean("2. Profilazione Etica dei Task"), ln=True)
        
        for node in nodes:
            p = node.profile
            if p:
                pdf.set_font("Arial", "B", 11)
                pdf.set_fill_color(230, 240, 255)
                pdf.cell(0, 8, clean(f" Task: {node.name}"), ln=True, fill=True)
                
                pdf.set_font("Arial", "", 9)
                origine = "BPMN" if p.is_automated else "AI"
                
                txt = (f"  - Origine Dati: {origine}\n"
                       f"  - Sensitive Data: {p.sensitive_data}\n"
                       f"  - Is Automated: {p.is_automated}\n"
                       f"  - Critical Task: {p.critical_task}\n"
                       f"  - Wellbeing Impact: {p.impacts_wellbeing}\n"
                       f"  - Criteria Defined: {p.criteria_defined}\n"
                       f"  - Off-Hours Risk: {p.outside_working_hours}")
                pdf.multi_cell(0, 5, clean(txt))
                pdf.ln(3)

        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean("3. Violazioni Rilevate (Rule Engine)"), ln=True)
        
        if not violations:
            pdf.set_font("Arial", "I", 11)
            pdf.cell(0, 10, "Nessuna violazione rilevata dal sistema.", ln=True)
        else:
            for v in violations:
                pdf.set_font("Arial", "B", 10)
                pdf.set_text_color(180, 0, 0)
                pdf.cell(0, 7, clean(f" {v.level.value}: {v.rule_name}"), ln=True)
                
                pdf.set_font("Arial", "", 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 5, clean(f" Task: {v.target_node}\n Messaggio: {v.message}"))
                pdf.ln(4)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean("4. Commento dell'Assistente AI"), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, clean(ai_feedback))

        pdf.output(output_path)