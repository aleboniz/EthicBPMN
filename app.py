import streamlit as st
import io
from src.parser import BpmnParser
from src.ai_complete import AICompleter
from src.rule_engine import EthicRuleEngine  # Usa il nome corretto della classe
from src.ai_assistant import AIAssistant
from src.reporter import ReportGenerator

# 1. CONFIGURAZIONE PAGINA (Deve essere la prima istruzione!)
st.set_page_config(page_title="EthicBPMN Auditor", layout="wide")

st.title("EthicBPMN: Audit Etico Automatizzato")
st.markdown("Carica il tuo file BPMN per analizzare la conformità all'AI Act e GDPR.")

# --- SIDEBAR PER IL CARICAMENTO ---
with st.sidebar:
    st.header("Configurazione")
    uploaded_file = st.file_uploader("Carica file .bpmn", type="bpmn")
    process_button = st.button("Avvia Analisi")

# --- LOGICA DI ELABORAZIONE ---
if uploaded_file and process_button:
    with st.spinner("Analisi in corso... attendere."):
        try:
            # 1. Parsing
            # Passiamo l'oggetto file direttamente al tuo parser
            parser = BpmnParser(uploaded_file)
            nodes = parser.parse()

            # 2. Inizializzazione Assistente e Completer
            # (Assicurati di avere la chiave API configurata o passata qui)
            ai_assistant = AIAssistant() 
            completer = AICompleter(ai_assistant)
            completer.complete_missing_profiles(nodes)

            # 3. Rule Engine & Metriche
            engine = EthicRuleEngine(nodes)
            violations = engine.run_all_rules()
            metrics = engine.calculate_eps_metrics()
            
            # 4. Feedback AI
            ai_feedback = ai_assistant.analyze_process_semantics(nodes)

            # 5. Risultati a video
            st.success("Analisi Completata!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("EPS Score", f"{metrics['eps']:.2f}")
            col2.metric("ERI Index", f"{metrics['eri']:.2f}")
            col3.metric("Violazioni", len(violations))

            # 6. Generazione Report (lo salva su disco come sempre)
            nome_file_report = "report_audit.md"
            ReportGenerator.generate_markdown(violations, ai_feedback, metrics, nodes, output_path=nome_file_report)

            # 7. Bottone di Download
            with open(nome_file_report, "rb") as file:
                st.download_button(
                    label="📥 Scarica Report Audit",
                    data=file,
                    file_name=nome_file_report,
                    mime="text/markdown"
                )
            
            # 8. Visualizzazione (Opzionale: vedi il report subito nell'app)
            with open(nome_file_report, "r", encoding="utf-8") as file:
                st.markdown("---")
                st.markdown(file.read())

        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {e}")