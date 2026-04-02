# src/reporter.py
from src.models import Violation
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def generate_markdown(violations: list[Violation], ai_feedback: str, metrics: dict, nodes: list,output_path: str = "ethicBPMN_report.md"):

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# EthicBPMN Audit Report\n")
            f.write(f"**Data Generazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Ethical Process Score \n")
            f.write(f"- **Maximum Risk (R_max):** `{metrics['r_max']}` (Rischio potenziale totale)\n")
            f.write(f"- **Observed Risk (R_obs):** `{metrics['r_obs']}` (Rischio delle violazioni trovate)\n")
            f.write(f"- **Ethical Risk Index (ERI):** `{metrics['eri']}`\n")
            
            # Formattazione condizionale del punteggio finale
            eps_score = metrics['eps']
                
            f.write(f"### Punteggio EPS Finale: {eps_score} / 1.00\n\n")
            f.write("---\n")
            # ------------------------------------------

            f.write("## Profilazione Etica dei Task (Audit Semantico)\n\n")
            f.write("In questa sezione sono riportati i parametri identificati per ogni attività del processo.\n\n")

            for node in nodes:
                p = node.profile
                if p:
                    origine = "BPMN" if p.is_automated else "AI"
                    
                    f.write(f"### Task: {node.name}\n")
                    f.write(f"- **Sensitive Data:** {p.sensitive_data}\n")
                    f.write(f"- **Is Automated:** {p.is_automated}\n")
                    f.write(f"- **Critical Task:** {p.critical_task}\n")
                    f.write(f"- **Wellbeing Impact:** {p.impacts_wellbeing}\n")
                    f.write(f"- **Criteria Defined:** {p.criteria_defined}\n")
                    f.write(f"- **Off-Hours Risk:** {p.outside_working_hours}\n\n")
            
            f.write("---\n")
            # -----------------------------------------------

            f.write("## Analisi Deterministica (Rule Engine)\n")
            if not violations:
                f.write("Nessuna violazione etica strutturale rilevata dal parser!\n")
            else:
                for v in violations:
                    f.write(f"### {v.level.value}\n")
                    f.write(f"- **Regola Violata:** {v.rule_number} - {v.rule_name}\n")
                    f.write(f"- **Nodo Interessato:** `{v.target_node}`\n")
                    f.write(f"- **Dettaglio:** {v.message}\n\n")
            
            f.write("---\n")
            f.write("## Analisi Semantica (LLM Assistant)\n")
            f.write(f"{ai_feedback}\n")
            
        print(f"Report salvato con successo in: {output_path}")
    