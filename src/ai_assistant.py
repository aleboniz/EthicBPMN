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

    def analyze_process_semantics(self, nodes: list[BpmnNode], custom_focus: str = "") -> str:
        if not self.client:
            return "OpenAI API Key non trovata. Analisi semantica saltata."

        process_summary = "Analizza questo processo BPMN per potenziali bias etici:\n"
        for node in nodes:
            process_summary += f"- Nodo: {node.name} (Tipo: {node.type_node})\n"

        # --- GESTIONE DEL FOCUS PERSONALIZZATO ---
        focus_instruction = ""
        if custom_focus.strip():
            focus_instruction = f"\n⚠️ DIRETTIVA DELL'UTENTE: L'utente ha richiesto di concentrare l'analisi specificamente su questo aspetto: '{custom_focus}'. Assicurati di dare massima priorità a questa tematica nella tua risposta.\n"

        prompt = f"""
        Sei un Auditor che analizza i principi etici dei processi aziendali (BPMN).
        Analizza le caratteristiche, i nomi e i tipi dei seguenti task. 
        Ricerca potenziali rischi etici tra cui privacy, supervisione umana, equità, discriminazione,
        responsabilità dei task, trasparenza, opacità, impatto sul benessere dei lavoratori, e altri.
        {focus_instruction}
        Fornisci un suggerimento breve (max 200 parole).
        
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
            return f"Errore durante l'analisi AI: {str(e)}"

    def generate_reengineering_proposals(self, nodes: list, violations: list, custom_focus: str = "") -> str:
        """Genera una proposta di reingegnerizzazione (modello TO-BE) basata sulle violazioni."""
        if not self.client:
            return "API LLM non disponibile. Modulo di reingegnerizzazione disabilitato."

        if not violations:
            return "🎉 **Il processo è già ottimizzato!**\nNon sono state rilevate violazioni strutturali o parametriche. Si consiglia di mantenere il monitoraggio continuo per assicurare che le performance etiche non decadano nel tempo."

        # Prepariamo il riassunto strutturale
        process_summary = "STRUTTURA DEL PROCESSO (AS-IS):\n"
        for node in nodes:
            process_summary += f"- Nodo: {node.name} (Tipo: {node.type_node})\n"

        # Prepariamo l'elenco dei "sintomi" (violazioni)
        violations_summary = "CRITICITÀ RILEVATE DAL RULE ENGINE:\n"
        for v in violations:
            violations_summary += f"- Regola {v.rule_number} ({v.rule_name}) violata sul task '{v.target_node}': {v.message}\n"

        # --- GESTIONE DEL FOCUS PERSONALIZZATO ---
        focus_instruction = ""
        if custom_focus.strip():
            focus_instruction = f"\n⚠️ DIRETTIVA DELL'UTENTE: Durante la riprogettazione, tieni in altissima considerazione questo focus o obiettivo specifico richiesto: '{custom_focus}'.\n"

        prompt = f"""
        Sei un Senior Business Process Engineer e un esperto di Etica dell'AI Act.
        Il seguente processo aziendale è stato analizzato e presenta alcune violazioni etiche.
        
        {process_summary}
        
        {violations_summary}
        {focus_instruction}
        
        Scrivi una "Proposta di Reingegnerizzazione (Modello TO-BE)" rivolta al Process Owner.
        Non limitarti a ripetere gli errori, ma suggerisci CONCRETAMENTE come ridisegnare il BPMN
        per risolvere i problemi (es. "aggiungere un User Task di revisione umana", 
        "inserire un Catch Event per i ricorsi", "dividere il task in due per minimizzare i dati").
        Sii schematico, professionale, orientato al business e usa elenchi puntati. 
        Mantieni la risposta sotto le 250 parole.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Errore durante la generazione della proposta: {str(e)}"
