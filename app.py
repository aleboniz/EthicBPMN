import streamlit as st
from src.parser import BpmnParser
from src.ai_complete import AICompleter
from src.rule_engine import EthicRuleEngine  
from src.ai_assistant import AIAssistant
from src.reporterpdf import PDFReportGenerator
from interface.bpmn_visualizer import visualizza_bpmn_interattivo


st.set_page_config(page_title="EthicBPMN Auditor", layout="wide")

st.title("EthicBPMN: Audit Etico Automatizzato")
st.markdown("Analisi della conformità ai principi etici dell'AI Act e del GDPR per processi BPMN.")

with st.sidebar:
    st.header("Configurazione")
    uploaded_file = st.file_uploader("Carica file .bpmn", type="bpmn")
    process_button = st.button("Avvia Analisi", use_container_width=True)

if uploaded_file and process_button:
    with st.spinner("Analisi in corso... attendere."):
        try:
            parser = BpmnParser(uploaded_file)
            nodes = parser.parse()

            ai_assistant = AIAssistant() 
            completer = AICompleter(ai_assistant)
            completer.complete_missing_profiles(nodes)

            engine = EthicRuleEngine(nodes)
            violations = engine.run_all_rules()
            metrics = engine.calculate_eps_metrics()
            
            ai_feedback = ai_assistant.analyze_process_semantics(nodes)

            st.success("Analisi Completata!")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("EPS Score", f"{metrics['eps']:.2f}")
            col2.metric("ERI Index", f"{metrics['eri']:.2f}")
            col3.metric("Violazioni Rilevate", len(violations))

            # --- STEP 1: VISUALIZZAZIONE PROCESSO ---
            st.divider()
            st.subheader("Mappa del Processo Analizzato")

            # Leggiamo il contenuto del file per il visualizzatore
            uploaded_file.seek(0)
            bpmn_xml_raw = uploaded_file.read().decode("utf-8")

            # Stampa i dati che stai mandando al visualizzatore per vedere cosa c'è dentro
            #st.write("Debug ID Violazioni:", [v.target_node for v in violations]) 

            # Chiamiamo la funzione che abbiamo creato sopra
            visualizza_bpmn_interattivo(bpmn_xml_raw, violations)
           
            st.divider()

            c_left, c_right = st.columns([3, 1])
            
            with c_left:
                st.subheader("Analisi dell'Assistente AI")
                st.info(ai_feedback)

            with c_right:
                st.subheader("📥 Esporta Report")
                nome_file_pdf = "report_audit.pdf"
                PDFReportGenerator.generate_pdf(violations, ai_feedback, metrics, nodes, output_path=nome_file_pdf)
                
                with open(nome_file_pdf, "rb") as f:
                    st.download_button(
                        label="Scarica Report PDF",
                        data=f,
                        file_name="Analisi_Etica_EthicBPMN.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            st.divider()
            with st.expander("🔍 Visualizza Dettagli Task (Profilazione Etica)"):
                for node in nodes:
                    if node.profile:
                        st.markdown(f"**Task:** `{node.name}`")
                        # Mostriamo i dati principali in una riga
                        d1, d2, d3, d4, d5, d6 = st.columns(6)
                        d1.write(f"**AI:** {node.profile.is_automated}")
                        d2.write(f"**Critical:** {node.profile.critical_task}")
                        d3.write(f"**Sensitive:** {node.profile.sensitive_data}")
                        d4.write(f"**Wellbeing:** {node.profile.impacts_wellbeing}")
                        d5.write(f"**Criteria:** {node.profile.criteria_defined}")
                        d6.write(f"**Off-Hours:** {node.profile.outside_working_hours}")
                        st.divider()

        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {e}")

