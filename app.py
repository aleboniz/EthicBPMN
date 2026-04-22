import streamlit as st
from src.parser import BpmnParser
from src.ai_complete import AICompleter
from src.rule_engine import EthicRuleEngine  
from src.ai_assistant import AIAssistant
from src.reporterpdf import PDFReportGenerator
from interface.bpmn_visualizer import visualizza_bpmn_interattivo
from src.bpmn_fixer import BpmnAutoFixer
from src.models import EquityAction 
import os

st.set_page_config(page_title="EthicBPMN Auditor", layout="wide")

st.markdown("""
    <style>
        /* Colori personalizzati opaci per le violazioni */
        .violation-error { background-color: rgba(255, 75, 75, 0.15); border-left: 5px solid #FF4B4B; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-warning { background-color: rgba(255, 140, 0, 0.15); border-left: 5px solid #FF8C00; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-suggestion { background-color: rgba(255, 204, 128, 0.25); border-left: 5px solid #FFCC80; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-info { background-color: rgba(255, 255, 0, 0.15); border-left: 5px solid #FFFF00; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("EthicBPMN: Audit Etico")
st.markdown("Analisi della conformità ai principi etici per processi BPMN.")

if 'stage' not in st.session_state:
    st.session_state.stage = 'upload'
if 'nodes' not in st.session_state:
    st.session_state.nodes = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'bpmn_xml_raw' not in st.session_state:
    st.session_state.bpmn_xml_raw = None

with st.sidebar:
    st.header("Configurazione")
    uploaded_file = st.file_uploader("Carica file .bpmn", type="bpmn")

    custom_focus = st.text_area(
        label="Focus Analisi (Opzionale)", 
        placeholder="Es: Concentrati sul rischio di discriminazione di genere...",
        help="Scrivi qui se vuoi che l'Intelligenza Artificiale presti particolare attenzione a un aspetto specifico del processo durante l'analisi semantica."
    )

    is_btn_disabled = (st.session_state.stage != 'upload') or (uploaded_file is None)
    
    process_button = st.button(
        "Avvia Analisi", 
        use_container_width=True, 
        disabled=is_btn_disabled
    )
    
    if st.session_state.stage != 'upload':
        if st.button("Nuova Analisi", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if st.session_state.stage == 'upload' and process_button:
    if uploaded_file is not None:
        raw_content = uploaded_file.read()
        st.session_state.bpmn_xml_raw = raw_content.decode("utf-8")
        with open("temp.bpmn", "wb") as f:
            f.write(raw_content)
        
        parser = BpmnParser("temp.bpmn")
        nodes = parser.parse()
        ai_assistant = AIAssistant() 
        completer = AICompleter(ai_assistant)
        completer.complete_missing_profiles(nodes)

        st.session_state.nodes = nodes
        st.session_state.stage = 'validation'
        st.rerun()

elif st.session_state.stage == 'validation':
    st.subheader("Revisione Profili Etici")
    st.info("Istruisci ogni elemento del processo (Task, Gateway ed Eventi) definendone le caratteristiche etiche.")
    
    with st.form(key="validation_form"):
        st.markdown("### Selezione Regole di Audit")
        st.caption("Seleziona quali regole includere nell'analisi. Di default sono tutte attive.")
        
        rule_names = {
            1: "R1: Privacy (Critica)", 2: "R2: Supervisione (Critica)", 3: "R3: Equità (Critica)", 4: "R4: Conflitto (Critica)",
            5: "R5: Anomalia (Alta)", 6: "R6: Neutralità (Alta)", 7: "R7: Responsabilità (Alta)",
            8: "R8: Appello (Media)", 9: "R9: Trasparenza (Media)",
            10: "R10: Benessere (Bassa)", 11: "R11: Proporzionalità (Bassa)", 12: "R12: Disconnessione (Bassa)"
        }
        
        active_rules = []
        r_cols = st.columns(4) # Creiamo 4 colonne per un layout compatto
        for i, (r_id, r_name) in enumerate(rule_names.items()):
            # Distribuiamo le checkbox sulle 4 colonne
            if r_cols[i % 4].checkbox(r_name, value=True, key=f"chk_rule_{r_id}"):
                active_rules.append(r_id)

        # Iteriamo su TUTTI i nodi estratti dal parser (inclusi eventi e gateway)
        for node in st.session_state.nodes:
            if hasattr(node, 'profile') and node.profile:
                st.markdown(f"### Elemento: `{node.name or node.id}`")
                st.caption(f"Tipo BPMN: {node.type_node}")
                
                b1, b2, b3, b4 = st.columns(4)
                node.profile.is_automated = b1.checkbox("Automatico", value=node.profile.is_automated, key=f"a_{node.id}")
                node.profile.critical_task = b2.checkbox("Critico", value=node.profile.critical_task, key=f"c_{node.id}")
                node.profile.sensitive_data = b3.checkbox("Dati Sensibili", value=node.profile.sensitive_data, key=f"s_{node.id}")
                node.profile.criteria_defined = b4.checkbox("Criteri Definiti", value=node.profile.criteria_defined, key=f"cd_{node.id}")
                
                node.profile.impacts_wellbeing = b1.checkbox("Benessere", value=node.profile.impacts_wellbeing, key=f"w_{node.id}")
                node.profile.outside_working_hours = b2.checkbox("Fuori Orario", value=node.profile.outside_working_hours, key=f"o_{node.id}")
                node.profile.default_action = b3.checkbox("Azione Default", value=node.profile.default_action, key=f"da_{node.id}")
                has_acc = b4.checkbox("Responsabile", value=bool(node.profile.acc_owner), key=f"h_acc_{node.id}")

                d1, d2 = st.columns(2)
                node.profile.type = d1.selectbox("Tipo Azione", ["Decision", "Assignment", "Execution", "Communication", "Evaluation"], index=2, key=f"t_{node.id}")
                eq_options = [e.name for e in EquityAction]
                current_eq_name = node.profile.equity_action.name if hasattr(node.profile.equity_action, 'name') else "NONE"
                selected_eq = d2.selectbox("Equity Action", eq_options, index=eq_options.index(current_eq_name) if current_eq_name in eq_options else 0, key=f"eq_{node.id}")
                node.profile.equity_action = EquityAction[selected_eq]

                i1, i2 = st.columns(2)
                node.profile.actor = i1.text_input("Attore / Esecutore", value=node.profile.actor or "", key=f"act_{node.id}")
                node.profile.beneficiary = i2.text_input("Beneficiari / Interessati", value=node.profile.beneficiary or "", key=f"ben_{node.id}")

                if has_acc:
                    node.profile.acc_owner = st.text_input("Accountability Owner (Responsabile)", value=node.profile.acc_owner or "", key=f"acc_name_{node.id}")
                else:
                    node.profile.acc_owner = None
                node.profile.equity_note = st.text_area("Note Etiche/Equità", value=node.profile.equity_note or "", height=80, key=f"eqn_{node.id}")
                st.markdown("---")
        
        submitted = st.form_submit_button("Conferma Parametri e Genera Audit", use_container_width=True)
    
    if submitted:
        engine = EthicRuleEngine(st.session_state.nodes)
        ai_assistant = AIAssistant()
        violations = engine.run_all_rules(active_rules=active_rules)

        reengineering = ai_assistant.generate_reengineering_proposals(
            st.session_state.nodes, 
            violations, 
            custom_focus=custom_focus,
            active_rules=active_rules
        )

        st.session_state.analysis_data = {
            'nodes': st.session_state.nodes,
            'violations': violations,
            'metrics': engine.calculate_eps_metrics(),
            'ai_feedback': ai_assistant.analyze_process_semantics(
                st.session_state.nodes, 
                custom_focus=custom_focus,
                active_rules=active_rules
            ),
            'reengineering': reengineering
        }
        st.session_state.stage = 'dashboard'
        st.rerun()

elif st.session_state.stage == 'dashboard' and st.session_state.analysis_data:
    st.components.v1.html("<script>window.parent.document.querySelector('.main').scrollTo(0,0);</script>", height=0)
    
    data = st.session_state.analysis_data
    
    if not os.path.exists("temp_process.bpmn") and st.session_state.bpmn_xml_raw:
        with open("temp_process.bpmn", "w", encoding="utf-8") as f:
            f.write(st.session_state.bpmn_xml_raw) 

    st.success("Analisi Completata!")
    col1, col2, col3 = st.columns(3)
    col1.metric("EPS Score", f"{data['metrics']['eps']:.2f}", help="Ethical Process Score (EPS): Livello di conformità globale. Tanto più il valore si avvicina a 1.00, tanto più il processo rispetta le regole etiche.")
    col2.metric("ERI Index", f"{data['metrics']['eri']:.2f}", help="Ethical Risk Index (ERI): Si calcola come quoziente tra le violazioni riscontrate e il rischio potenziale massimo del processo, sulla base delle regole valutate.")
    col3.metric("Violazioni Rilevate", len(data['violations']), help="Numero totale di criticità etiche riscontrate.")

    st.divider()
    visualizza_bpmn_interattivo(st.session_state.bpmn_xml_raw, data['violations'])
    
    st.divider()
    st.subheader("Dettaglio Regole Violate")

    v_map = {}
    for v in data['violations']:
        v_map.setdefault(v.target_node, []).append(v)

    if not v_map:
        st.success("Nessuna violazione rilevata. Il processo rispetta i criteri definiti.")
    else:
        for t_id, v_list in v_map.items():
            node = next((n for n in data['nodes'] if n.id == t_id), None)
            t_name = node.name if node and node.name else t_id
            with st.expander(f"Elemento: {t_name}"):
                for v in v_list:
                    lvl = v.level.name.upper()
                    style_class = "violation-error" if lvl == "ERROR" else "violation-warning" if lvl == "WARNING" else "violation-suggestion" if lvl == "SUGGESTION" else "violation-info"
                    st.markdown(f'<div class="{style_class}"><b>Regola {v.rule_number}: {v.rule_name}</b><br><small>{v.message}</small></div>', unsafe_allow_html=True)

    st.divider()
    cl, cr = st.columns([3, 1])
    with cl:
        st.subheader("Analisi dell'Assistente AI")
        if custom_focus and custom_focus.strip():
            st.caption(f"**Focus richiesto:** *{custom_focus}*")
        st.info(data['ai_feedback'])

        st.subheader("Proposte di Reingegnerizzazione (Modello TO-BE)")
        st.success(data.get('reengineering', "Nessuna proposta disponibile."))

    with cr:
        st.subheader("Esporta Dati")
        reeng_text = data.get('reengineering', "Nessuna proposta disponibile.")
        PDFReportGenerator.generate_pdf(data['violations'], data['ai_feedback'], data['metrics'], data['nodes'], reeng_text, "report_audit.pdf")
        with open("report_audit.pdf", "rb") as f:
            st.download_button("Scarica Report PDF", f, "Analisi_Etica_EthicBPMN.pdf", use_container_width=True)
        
        BpmnAutoFixer.generate_fixed_bpmn("temp_process.bpmn", data['nodes'], "Corrected_process.bpmn")
        with open("Corrected_process.bpmn", "rb") as f:
            st.download_button("Scarica BPMN Corretto", f, "Corrected_process.bpmn", use_container_width=True)

    st.divider()
    with st.expander("Verifica Parametri Inseriti", expanded=False):
        for node in data['nodes']:
            if node.profile:
                st.markdown(f"#### Elemento: `{node.name or node.id}`")
                v1, v2 = st.columns(2)
                v1.write(f"**Attore:** {node.profile.actor or 'N/A'} | **Beneficiari:** {node.profile.beneficiary or 'N/A'}")
                v2.write(f"**Tipo:** {node.profile.type} | **Equity:** {node.profile.equity_action.name}")
                st.divider()

                