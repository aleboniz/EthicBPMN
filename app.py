import streamlit as st
from src.parser import BpmnParser
from src.ai_complete import AICompleter
from src.rule_engine import EthicRuleEngine  
from src.ai_assistant import AIAssistant
from src.reporterpdf import PDFReportGenerator
from interface.bpmn_visualizer import visualizza_bpmn_interattivo
from src.bpmn_fixer import BpmnAutoFixer


st.set_page_config(page_title="EthicBPMN Auditor", layout="wide")

st.title("EthicBPMN: Audit Etico Automatizzato")
st.markdown("Analisi della conformità ai principi etici dell'AI Act e del GDPR per processi BPMN.")

with st.sidebar:
    st.header("Configurazione")
    uploaded_file = st.file_uploader("Carica file .bpmn", type="bpmn")
    process_button = st.button("Avvia Analisi", use_container_width=True)

# --- 1. Inizializzazione della Memoria ---
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# --- 2. Esecuzione dell'Analisi (Avviene SOLO quando si clicca Avvia) ---
if process_button:
    with st.spinner("Analisi in corso..."):
        try:
            parser = BpmnParser(uploaded_file) # Usa uploaded_file o il default
            nodes = parser.parse()

            ai_assistant = AIAssistant() 
            completer = AICompleter(ai_assistant)
            completer.complete_missing_profiles(nodes)

            engine = EthicRuleEngine(nodes)
            violations = engine.run_all_rules()
            metrics = engine.calculate_eps_metrics()
            
            ai_feedback = ai_assistant.analyze_process_semantics(nodes)

            # SALVIAMO I RISULTATI NELLA MEMORIA DI STREAMLIT
            st.session_state.analysis_data = {
                'nodes': nodes,
                'violations': violations,
                'metrics': metrics,
                'ai_feedback': ai_feedback,
                'bpmn_target': uploaded_file
            }
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {e}")

# --- 3. Disegno della Dashboard (Legge dalla Memoria) ---
if st.session_state.analysis_data is not None:
    # Estraiamo i dati dalla memoria
    data = st.session_state.analysis_data
    nodes = data['nodes']
    violations = data['violations']
    metrics = data['metrics']
    ai_feedback = data['ai_feedback']
    bpmn_target = data['bpmn_target']

    st.success("Analisi Completata!")
    
    # Metriche Superiori
    col1, col2, col3 = st.columns(3)
    col1.metric("EPS Score", f"{metrics['eps']:.2f}")
    col2.metric("ERI Index", f"{metrics['eri']:.2f}")
    col3.metric("Violazioni Rilevate", len(violations))

    st.divider()
    st.subheader("Mappa del Processo Analizzato")

    # Gestione del file per la mappa
    if hasattr(bpmn_target, 'seek'):
        bpmn_target.seek(0)
        bpmn_xml_raw = bpmn_target.read().decode("utf-8")
    else:
        with open(bpmn_target, "r", encoding="utf-8") as f:
            bpmn_xml_raw = f.read()

    visualizza_bpmn_interattivo(bpmn_xml_raw, violations)
    
    st.divider()

    c_left, c_right = st.columns([3, 1])
    
    with c_left:
        st.subheader("Analisi dell'Assistente AI")
        st.info(ai_feedback)

    with c_right:
        st.subheader("Esporta Dati")
        
        # --- PDF ---
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
        
        # --- BPMN FIXATO ---
        nome_file_bpmn = "Processo_Ethic_Fixed.bpmn"
        if hasattr(bpmn_target, 'seek'):
            bpmn_target.seek(0)
        BpmnAutoFixer.generate_fixed_bpmn(bpmn_target, nodes, output_path=nome_file_bpmn)
        with open(nome_file_bpmn, "rb") as f:
            st.download_button(
                label="Scarica BPMN Corretto",
                data=f,
                file_name=nome_file_bpmn,
                mime="text/xml",
                use_container_width=True
            )

    st.divider()
    with st.expander("Visualizza Dettagli Task"):
        for node in nodes:
            if node.profile:
                st.markdown(f"**Task:** `{node.name}`")
                d1, d2, d3, d4, d5, d6 = st.columns(6)
                d1.write(f"**AI:** {node.profile.is_automated}")
                d2.write(f"**Critical:** {node.profile.critical_task}")
                d3.write(f"**Sensitive:** {node.profile.sensitive_data}")
                d4.write(f"**Wellbeing:** {node.profile.impacts_wellbeing}")
                d5.write(f"**Criteria:** {node.profile.criteria_defined}")
                d6.write(f"**Off-Hours:** {node.profile.outside_working_hours}")
                st.divider()