# src/ai_assistant.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.models import BpmnNode

class AIAssistant:
    def __init__(self):
        load_dotenv(override=True) 
        # Inizializzazione del client OpenAI leggendo
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1" 
                )
        else:
            self.client = None

    def _get_active_rule_names(self, active_rules: list, lang: str = "ITA") -> str:
        """Traduce gli ID delle regole nei concetti etici corrispondenti per il prompt LLM."""
        if lang == "ITA":
            if not active_rules or len(active_rules) == 12:
                return "Tutte le direttive etiche dell'AI Act (Privacy, Equità, Supervisione, Trasparenza, ecc.)."
            rule_map = {
                1: "Privacy e Minimizzazione dei Dati",
                2: "Supervisione Umana (Human-in-the-loop)",
                3: "Equità e Antidiscriminazione",
                4: "Prevenzione del Conflitto di Interessi",
                5: "Controlli sulle Anomalie",
                6: "Neutralità Algoritmica",
                7: "Accountability e Responsabilità",
                8: "Diritto di Appello e Ricorso",
                9: "Trasparenza e Spiegabilità",
                10: "Benessere Cognitivo e Pause",
                11: "Proporzionalità del Monitoraggio",
                12: "Diritto alla Disconnessione"
            }
        else:
            if not active_rules or len(active_rules) == 12:
                return "All AI Act ethical directives (Privacy, Fairness, Oversight, Transparency, etc.)."
            rule_map = {
                1: "Privacy and Data Minimization",
                2: "Human Oversight (Human-in-the-loop)",
                3: "Fairness and Anti-discrimination",
                4: "Prevention of Conflict of Interest",
                5: "Anomaly Controls",
                6: "Algorithmic Neutrality",
                7: "Accountability and Responsibility",
                8: "Right to Appeal and Recourse",
                9: "Transparency and Explainability",
                10: "Cognitive Well-being and Breaks",
                11: "Proportionality of Monitoring",
                12: "Right to Disconnect"
            }
        selections = [rule_map[r] for r in active_rules if r in rule_map]
        return ", ".join(selections)

    def analyze_process_semantics(self, nodes: list[BpmnNode], custom_focus: str = "", active_rules: list = None, lang: str = "ITA") -> str:
        if not self.client:
            return "OpenAI API Key non trovata. Analisi semantica saltata." if lang == "ITA" else "OpenAI API Key not found. Semantic analysis skipped."

        node_label = "Nodo" if lang == "ITA" else "Node"
        type_label = "Tipo" if lang == "ITA" else "Type"
        
        process_summary = "Analizza questo processo BPMN per potenziali bias etici:\n" if lang == "ITA" else "Analyze this BPMN process for potential ethical biases:\n"
        for node in nodes:
            process_summary += f"- {node_label}: {node.name} ({type_label}: {node.type_node})\n"

        scope_text = self._get_active_rule_names(active_rules, lang=lang)

        if lang == "ITA":
            active_rules_summary = f"SCOPE DI AUDIT (REGOLE DA CONTROLLARE):\nL'analisi deve limitarsi ESCLUSIVAMENTE a queste tematiche:\n- " + "\n- ".join(scope_text.split(", "))
            focus_instruction = ""
            if custom_focus.strip():
                focus_instruction = f"\nDIRETTIVA DELL'UTENTE: L'utente ha richiesto di concentrare l'analisi specificamente su questo aspetto: '{custom_focus}'. Assicurati di dare massima priorità a questa tematica nella tua risposta.\n"

            prompt = f"""
            Sei un Auditor che analizza i principi etici dei processi aziendali (BPMN).
            Analizza le caratteristiche, i nomi e i tipi dei seguenti task. 
            Ricerca potenziali rischi etici valutando: {active_rules_summary}
            {focus_instruction}
            Fornisci un suggerimento breve (max 200 parole).
            {process_summary}
            """
        else:
            active_rules_summary = f"AUDIT SCOPE (RULES TO CHECK):\nThe analysis must be LIMITED to these topics:\n- " + "\n- ".join(scope_text.split(", "))
            focus_instruction = ""
            if custom_focus.strip():
                focus_instruction = f"\nUSER DIRECTIVE: The user has requested to focus the analysis specifically on this aspect: '{custom_focus}'. Ensure you give maximum priority to this theme in your response.\n"

            prompt = f"""
            You are an Auditor analyzing the ethical principles of business processes (BPMN).
            Analyze the characteristics, names, and types of the following tasks. 
            Search for potential ethical risks by evaluating: {active_rules_summary}
            {focus_instruction}
            Provide a brief suggestion (max 200 words).
            {process_summary}
            """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Errore: {str(e)}" if lang == "ITA" else f"Error: {str(e)}"

    def generate_reengineering_proposals(self, nodes: list, violations: list, custom_focus: str = "", active_rules: list = None, lang: str = "ITA") -> str:
        """Genera una proposta di reingegnerizzazione (modello TO-BE) basata sulle violazioni."""
        if not self.client:
            return "API LLM non disponibile." if lang == "ITA" else "LLM API not available."

        if not violations:
            if lang == "ITA":
                return "**Il processo è già ottimizzato!**\nNon sono state rilevate violazioni strutturali o parametriche."
            else:
                return "**The process is already optimized!**\nNo structural or parametric violations were detected."

        node_label = "Nodo" if lang == "ITA" else "Node"
        type_label = "Tipo" if lang == "ITA" else "Type"
        
        process_summary = "STRUTTURA DEL PROCESSO (AS-IS):\n" if lang == "ITA" else "PROCESS STRUCTURE (AS-IS):\n"
        for node in nodes:
            process_summary += f"- {node_label}: {node.name} ({type_label}: {node.type_node})\n"

        violations_summary = "CRITICITÀ RILEVATE DAL RULE ENGINE:\n" if lang == "ITA" else "CRITICALITIES DETECTED BY THE RULE ENGINE:\n"
        for v in violations:
            if lang == "ITA":
                violations_summary += f"- Regola {v.rule_number} ({v.rule_name}) violata sul task '{v.target_node}': {v.message}\n"
            else:
                violations_summary += f"- Rule {v.rule_number} ({v.rule_name}) violated on task '{v.target_node}': {v.message}\n"

        scope_text = self._get_active_rule_names(active_rules, lang=lang)

        if lang == "ITA":
            active_rules_summary = f"SCOPE DI AUDIT (REGOLE DA RISOLVERE):\nLe tue proposte devono coprire ESCLUSIVAMENTE queste tematiche:\n- " + "\n- ".join(scope_text.split(", "))
            focus_instruction = f"\nDIRETTIVA DELL'UTENTE: Durante la riprogettazione, tieni in altissima considerazione questo focus: '{custom_focus}'.\n" if custom_focus.strip() else ""

            prompt = f"""
            Sei un Senior Business Process Engineer e un esperto di Etica dell'AI Act.
            Il seguente processo aziendale presenta alcune violazioni etiche.
            {process_summary}
            {violations_summary}
            {focus_instruction}
            Scrivi una "Proposta di Reingegnerizzazione (Modello TO-BE)" rivolta al Process Owner.
            Suggerisci CONCRETAMENTE come ridisegnare il BPMN per risolvere i problemi relativamente a {active_rules_summary}
            (es. "aggiungere un User Task di revisione umana", ecc.).
            Sii schematico, professionale e usa elenchi puntati. Max 250 parole.
            """
        else:
            active_rules_summary = f"AUDIT SCOPE (RULES TO RESOLVE):\nYour proposals must EXCLUSIVELY cover these themes:\n- " + "\n- ".join(scope_text.split(", "))
            focus_instruction = f"\nUSER DIRECTIVE: During redesign, give high consideration to this specific focus: '{custom_focus}'.\n" if custom_focus.strip() else ""

            prompt = f"""
            You are a Senior Business Process Engineer and an AI Act Ethics expert.
            The following business process presents some ethical violations.
            {process_summary}
            {violations_summary}
            {focus_instruction}
            Write a "Re-engineering Proposal (TO-BE Model)" addressed to the Process Owner.
            Suggest CONCRETELY how to redesign the BPMN to solve problems related to {active_rules_summary}
            (e.g., "add a human review User Task", etc.).
            Be schematic, professional, business-oriented and use bullet points. Max 250 words.
            """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Errore: {str(e)}" if lang == "ITA" else f"Error: {str(e)}"