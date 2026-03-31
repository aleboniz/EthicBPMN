# src/ai_assistant.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.models import BpmnNode

class AIAssistant:
    def __init__(self):
        load_dotenv(override=True)  # <-- 2. AGGIUNGI QUESTA RIGA (Carica i dati dal file .env)
        
        # Inizializza il client OpenAI leggendo la variabile d'ambiente
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1" # Diciamo alla libreria di puntare a Groq!
                )
        else:
            self.client = None

    def analyze_process_semantics(self, nodes: list[BpmnNode]) -> str:
        if not self.client:
            return "OpenAI API Key non trovata. Analisi semantica saltata."

        # Prepariamo un riassunto testuale del processo per l'AI
        process_summary = "Analizza questo processo BPMN per potenziali bias etici:\n"
        for node in nodes:
            process_summary += f"- Nodo: {node.name} (Tipo: {node.type_node})\n"

        prompt = f"""
        Sei un Auditor Etico specializzato in processi aziendali (BPMN).
        Analizza i nomi e i tipi dei seguenti task. Trova potenziali rischi di discriminazione,
        opacità o impatto sul benessere dei lavoratori non strutturali, ma semantici.
        Fornisci un suggerimento breve e puntuale (max 150 parole).
        
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