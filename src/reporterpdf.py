from fpdf import FPDF
from datetime import datetime

class PDFReportGenerator:
    @staticmethod
    def generate_pdf(violations, ai_feedback, metrics, nodes, reengineering_proposals, output_path="report_audit.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        PRIMARY_BLUE = (20, 40, 80)
        LIGHT_BLUE = (235, 240, 245)
        TEXT_DARK = (33, 37, 41)
        BG_LIGHT = (248, 249, 250)

        def clean(text):
            if text is None: return "N/A"
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        pdf.set_fill_color(*PRIMARY_BLUE)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "EthicBPMN Audit Report", ln=True, align='C')
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, f"Report generato il: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='C')
        pdf.ln(20)

        pdf.set_text_color(*TEXT_DARK)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Valutazione Sintetica", ln=True)
        
        pdf.ln(2)
        rect_w = 190
        rect_h = 25
        rect_x = 10
        y_box = pdf.get_y()
        
        pdf.set_fill_color(*BG_LIGHT)
        pdf.set_draw_color(*PRIMARY_BLUE)
        pdf.rect(rect_x, y_box, rect_w, rect_h, 'FD')
        
        pdf.set_y(y_box + 8)
        pdf.set_font("Arial", "B", 12)
        num_violations = len(violations) if violations else 0
        col_w_box = rect_w / 3
        
        pdf.set_x(rect_x)
        pdf.cell(col_w_box, 8, f"EPS SCORE: {metrics.get('eps', '0')}", align='C')
        pdf.cell(col_w_box, 8, f"ERI INDEX: {metrics.get('eri', '0')}", align='C')
        pdf.cell(col_w_box, 8, f"VIOLAZIONI: {num_violations}", align='C', ln=True)
        
        pdf.set_y(y_box + rect_h + 10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. Dettaglio Profilazione Task", ln=True)
        
        for node in nodes:
            p = node.profile
            if p:
                pdf.set_fill_color(*LIGHT_BLUE)
                pdf.set_font("Arial", "B", 10)
                pdf.set_text_color(*PRIMARY_BLUE)
                pdf.cell(0, 8, clean(f"  TASK: {node.name or node.id}"), ln=True, fill=True)
                
                pdf.set_text_color(*TEXT_DARK)
                pdf.set_font("Arial", "", 9)
                
                y_task_start = pdf.get_y() + 2
                pdf.set_y(y_task_start)
                
                col_w = 90
                
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- Automatico: {'SI' if p.is_automated else 'NO'}"), ln=True)
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- Task Critico: {'SI' if p.critical_task else 'NO'}"), ln=True)
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- Dati Sensibili: {'SI' if p.sensitive_data else 'NO'}"), ln=True)
                
                y_after_left = pdf.get_y()
                
                pdf.set_xy(105, y_task_start)
                pdf.cell(col_w, 5, clean(f"- Impatto Benessere: {'SI' if p.impacts_wellbeing else 'NO'}"), ln=True)
                pdf.set_x(105)
                pdf.cell(col_w, 5, clean(f"- Criteri Definiti: {'SI' if p.criteria_defined else 'NO'}"), ln=True)
                pdf.set_x(105)
                pdf.cell(col_w, 5, clean(f"- Fuori Orario: {'SI' if p.outside_working_hours else 'NO'}"), ln=True)
                
                final_y = max(y_after_left, pdf.get_y())
                pdf.set_y(final_y + 2)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 10, "3. Analisi Violazioni Rilevate", ln=True)
        
        if not violations:
            pdf.set_font("Arial", "I", 11)
            pdf.cell(0, 10, "Nessuna violazione rilevata.", ln=True)
        else:
            for v in violations:
                lvl = v.level.name.upper() if hasattr(v.level, 'name') else str(v.level).upper()
                
                if "ERROR" in lvl:
                    pdf.set_text_color(220, 53, 41)    
                elif "WARNING" in lvl:
                    pdf.set_text_color(255, 69, 0)    
                elif "INFO" in lvl:
                    pdf.set_text_color(255, 165, 0)  
                elif "SUGGESTION" in lvl:
                    pdf.set_text_color(218, 165, 32)  
                else:
                    pdf.set_text_color(*TEXT_DARK)   

                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 7, clean(f" {lvl}: {v.rule_name}"), ln=True)
                
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(*TEXT_DARK)
                pdf.multi_cell(0, 5, clean(f" Elemento: {v.target_node}\n Messaggio: {v.message}"), border="L")
                pdf.ln(3)

        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "4. Parere dell'Assistente AI", ln=True, fill=True)
        pdf.set_font("Arial", "", 10) 
        pdf.multi_cell(0, 6, clean(ai_feedback))

        pdf.ln(8)
        pdf.set_fill_color(230, 245, 230) # Sfondo verde
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean("5. Proposte di Reingegnerizzazione (Modello TO-BE)"), ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(2)
        clean_proposal = str(reengineering_proposals).replace("**", "").replace("#", "")
        pdf.multi_cell(0, 6, clean(clean_proposal))

        pdf.output(output_path)