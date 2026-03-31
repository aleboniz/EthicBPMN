# src/reporter.py
from src.models import Violation
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def generate_markdown(violations: list[Violation], ai_feedback: str, output_path: str = "ethicBPMN_report.md"):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# EthicBPMN Audit Report\n")
            f.write(f"**Data Generazione:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Analisi Deterministica (Rule Engine)\n")
            if not violations:
                f.write(" Nessuna violazione etica strutturale rilevata dal parser!\n")
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