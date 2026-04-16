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

    def analyze_process_semantics(self, nodes: list[BpmnNode]) -> str:
        if not self.client:
            return "OpenAI API Key non trovata. Analisi semantica saltata."

        # Preparazione del riassunto testuale del processo per l'AI
        process_summary = "Analizza questo processo BPMN per potenziali bias etici:\n"
        for node in nodes:
            process_summary += f"- Nodo: {node.name} (Tipo: {node.type_node})\n"

        prompt = f"""
        Sei un Auditor che analizza i principi etici dei processi aziendali (BPMN).
        Analizza le caratteristiche, i nomi e i tipi dei seguenti task. 
        Ricerca potenziali rischi etici tra cui privacy, supervisione umana, equità, discriminazione,
        responsabilità dei task, trasparenza, opacità, impatto sul benessere dei lavoratori, e altri.
        Fornisci un suggerimento breve e puntuale (max 200 parole).
        
        {process_summary}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # Modello gratuito
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Errore durante la chiamata ad OpenAI: {str(e)}"