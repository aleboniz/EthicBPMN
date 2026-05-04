#src/reporterpdf.py
from fpdf import FPDF
from datetime import datetime

class PDFReportGenerator:
    @staticmethod
    def generate_pdf(violations, ai_feedback, metrics, nodes, reengineering_proposals, output_path="report_audit.pdf", lang="ITA"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        T = {
            'ITA': {
                'title': "EthicBPMN Audit Report",
                'gen_date': "Report generato il:",
                'sec_1': "1. Valutazione Sintetica",
                'sec_2': "2. Dettaglio Profilazione Task",
                'sec_3': "3. Analisi Violazioni Rilevate",
                'sec_4': "4. Parere dell'Assistente AI",
                'sec_5': "5. Proposte di Reingegnerizzazione (Modello TO-BE)",
                'violations': "VIOLAZIONI",
                'task': "TASK",
                'auto': "Automatico",
                'crit': "Task Critico",
                'sens': "Dati Sensibili",
                'well': "Impatto Benessere",
                'def': "Criteri Definiti",
                'off': "Fuori Orario",
                'no_viol': "Nessuna violazione rilevata.",
                'elem': "Elemento",
                'msg': "Messaggio",
                'yes': "SI",
                'no': "NO"
            },
            'ENG': {
                'title': "EthicBPMN Audit Report",
                'gen_date': "Report generated on:",
                'sec_1': "1. Summary Assessment",
                'sec_2': "2. Task Profiling Detail",
                'sec_3': "3. Detected Violations Analysis",
                'sec_4': "4. AI Assistant Opinion",
                'sec_5': "5. Re-engineering Proposals (TO-BE Model)",
                'violations': "VIOLATIONS",
                'task': "TASK",
                'auto': "Automated",
                'crit': "Critical Task",
                'sens': "Sensitive Data",
                'well': "Well-being Impact",
                'def': "Defined Criteria",
                'off': "Off-hours",
                'no_viol': "No violations detected.",
                'elem': "Element",
                'msg': "Message",
                'yes': "YES",
                'no': "NO"
            }
        }[lang]

        PRIMARY_BLUE = (20, 40, 80)
        LIGHT_BLUE = (235, 240, 245)
        TEXT_DARK = (33, 37, 41)
        BG_LIGHT = (248, 249, 250)

        def clean(text):
            if text is None: return "N/A"
            text = str(text).replace("**", "").replace("###", "").replace("#", "").replace("+ ", "- ")
            return text.encode('latin-1', 'replace').decode('latin-1')

        pdf.set_fill_color(*PRIMARY_BLUE)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, T['title'], ln=True, align='C')
        pdf.set_font("Arial", "", 10)
        
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        pdf.cell(0, 5, f"{T['gen_date']} {date_str}", ln=True, align='C')
        pdf.ln(20)

        pdf.set_text_color(*TEXT_DARK)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, T['sec_1'], ln=True)
        
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
        pdf.cell(col_w_box, 8, f"{T['violations']}: {num_violations}", align='C', ln=True)
        
        pdf.set_y(y_box + rect_h + 10)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, T['sec_2'], ln=True)
        
        for node in nodes:
            p = node.profile
            if p:
                pdf.set_fill_color(*LIGHT_BLUE)
                pdf.set_font("Arial", "B", 10)
                pdf.set_text_color(*PRIMARY_BLUE)
                pdf.cell(0, 8, clean(f"  {T['task']}: {node.name or node.id}"), ln=True, fill=True)
                
                pdf.set_text_color(*TEXT_DARK)
                pdf.set_font("Arial", "", 9)
                
                y_task_start = pdf.get_y() + 2
                pdf.set_y(y_task_start)
                
                col_w = 90
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- {T['auto']}: {T['yes'] if p.is_automated else T['no']}"), ln=True)
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- {T['crit']}: {T['yes'] if p.critical_task else T['no']}"), ln=True)
                pdf.set_x(15)
                pdf.cell(col_w, 5, clean(f"- {T['sens']}: {T['yes'] if p.sensitive_data else T['no']}"), ln=True)
                
                y_after_left = pdf.get_y()
                pdf.set_xy(105, y_task_start)
                pdf.cell(col_w, 5, clean(f"- {T['well']}: {T['yes'] if p.impacts_wellbeing else T['no']}"), ln=True)
                pdf.set_x(105)
                pdf.cell(col_w, 5, clean(f"- {T['def']}: {T['yes'] if p.criteria_defined else T['no']}"), ln=True)
                pdf.set_x(105)
                pdf.cell(col_w, 5, clean(f"- {T['off']}: {T['yes'] if p.outside_working_hours else T['no']}"), ln=True)
                
                final_y = max(y_after_left, pdf.get_y())
                pdf.set_y(final_y + 2)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 10, T['sec_3'], ln=True)
        
        if not violations:
            pdf.set_font("Arial", "I", 11)
            pdf.cell(0, 10, T['no_viol'], ln=True)
        else:
            for v in violations:
                nome_leggibile = v.target_node
                if nodes:
                    for nodo in nodes:
                        if nodo.id == v.target_node:
                            if nodo.name and nodo.name.strip():
                                nome_leggibile = nodo.name
                            break 

                lvl = v.level.name.upper() if hasattr(v.level, 'name') else str(v.level).upper()
                if "ERROR" in lvl: pdf.set_text_color(220, 53, 41)    
                elif "WARNING" in lvl: pdf.set_text_color(255, 69, 0)    
                elif "INFO" in lvl: pdf.set_text_color(255, 165, 0)  
                elif "SUGGESTION" in lvl: pdf.set_text_color(218, 165, 32)  
                else: pdf.set_text_color(0, 0, 0)   

                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 7, clean(f" {lvl}: {v.rule_name}"), ln=True)
                pdf.set_font("Arial", "", 9)
                pdf.set_text_color(50, 50, 50)
                
                testo_dettaglio = f" {T['elem']}: {nome_leggibile}\n {T['msg']}: {v.message}"
                pdf.multi_cell(0, 5, clean(testo_dettaglio), border="L")
                pdf.ln(3)

        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 10, T['sec_4'], ln=True, fill=True)
        pdf.set_font("Arial", "", 10) 
        pdf.multi_cell(0, 6, clean(ai_feedback))

        pdf.ln(8)
        pdf.set_fill_color(230, 245, 230)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, clean(T['sec_5']), ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(2)
        pdf.multi_cell(0, 6, clean(reengineering_proposals))

        pdf.output(output_path)