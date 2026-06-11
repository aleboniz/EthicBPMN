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

if 'lang' not in st.session_state:
    st.session_state.lang = 'ITA'
if 'stage' not in st.session_state:
    st.session_state.stage = 'upload'
if 'nodes' not in st.session_state:
    st.session_state.nodes = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'bpmn_xml_raw' not in st.session_state:
    st.session_state.bpmn_xml_raw = None

translations = {
    'ITA': {
        'lang_btn': "🇬🇧 ENG",
        'title': "EthicBPMN: Audit Etico",
        'subtitle': "Analisi della conformità ai principi etici per processi BPMN.",
        'sidebar_header': "Configurazione",
        'upload_label': "Carica file .bpmn",
        'focus_label': "Focus Analisi (Opzionale)",
        'focus_ph': "Es: Concentrati sul rischio di discriminazione di genere...",
        'focus_help': "Scrivi qui se vuoi che l'IA presti attenzione a un aspetto specifico.",
        'btn_start': "Avvia Analisi",
        'btn_new': "Nuova Analisi",
        'sub_rev': "Revisione Profili Etici",
        'audit_sel': "Selezione Regole di Audit",
        'audit_cap': "Seleziona quali regole includere nell'analisi. Di default sono tutte attive.",
        'element': "Elemento",
        'node_auto': "Automatico",
        'node_crit': "Critico",
        'node_sens': "Dati Sensibili",
        'node_def': "Criteri Definiti",
        'node_well': "Benessere",
        'node_off': "Fuori Orario",
        'node_da': "Azione Default",
        'node_acc': "Responsabile",
        'node_type': "Tipo Azione",
        'node_act': "Attore / Esecutore",
        'node_ben': "Beneficiari / Interessati",
        'node_eqn': "Tipologia di Supporto/Equità",
        'equity_label': "Azione di Equità",
        'btn_audit': "Conferma Parametri e Genera Audit",
        'success': "Analisi Completata!",
        'viol_detail': "Dettaglio Regole Violate",
        'no_viol': "Nessuna violazione rilevata. Il processo rispetta i criteri definiti.",
        'viol_help': "Numero delle violazioni rilevate.",
        'ai_header': "Analisi dell'Assistente AI",
        'reeng_header': "Proposte di Reingegnerizzazione (Modello TO-BE)",
        'export_header': "Esporta Dati",
        'btn_pdf': "Scarica Report PDF",
        'btn_bpmn': "Scarica BPMN Corretto",
        'verify_header': "Verifica Parametri Inseriti",
        'eps_label': "Punteggio EPS",
        'eri_label': "Indice ERI",
        'eps_help': "Ethical Process Score: Livello di conformità globale. Il valore massimo è 1.00.",
        'eri_help': "Ethical Risk Index: Rapporto tra violazioni e rischio potenziale massimo.",
        'rule_prefix': "Regola",
        'rules': {
            1: "R1: Privacy", 2: "R2: Supervisione", 3: "R3: Equità", 4: "R4: Conflitto",
            5: "R5: Anomalia", 6: "R6: Neutralità", 7: "R7: Responsabilità",
            8: "R8: Appello", 9: "R9: Trasparenza",
            10: "R10: Benessere", 11: "R11: Proporzionalità", 12: "R12: Disconnessione"
        }
    },
    'ENG': {
        'lang_btn': "🇮🇹 ITA",
        'title': "EthicBPMN: Ethical Audit",
        'subtitle': "Compliance analysis with ethical principles for BPMN processes.",
        'sidebar_header': "Configuration",
        'upload_label': "Upload .bpmn file",
        'focus_label': "Analysis Focus (Optional)",
        'focus_ph': "E.g.: Focus on gender discrimination risk...",
        'focus_help': "Write here if you want the AI to pay attention to a specific aspect.",
        'btn_start': "Start Analysis",
        'btn_new': "New Analysis",
        'sub_rev': "Ethical Profiles Review",
        'audit_sel': "Audit Rules Selection",
        'audit_cap': "Select which rules to include. Default: all active.",
        'element': "Element",
        'node_auto': "Automated",
        'node_crit': "Critical",
        'node_sens': "Sensitive Data",
        'node_def': "Defined Criteria",
        'node_well': "Well-being",
        'node_off': "Off-hours",
        'node_da': "Default Action",
        'node_acc': "Accountable",
        'node_type': "Action Type",
        'node_act': "Actor / Executor",
        'node_ben': "Beneficiaries / Stakeholders",
        'node_eqn': "Support/Equity Type",
        'equity_label': "Equity Action",
        'btn_audit': "Confirm Parameters and Generate Audit",
        'success': "Analysis Completed!",
        'viol_detail': "Violated Rules Detail",
        'no_viol': "No violations detected. The process complies with the criteria.",
        'viol_help': "Number of detected violations, visible in the panels below.",
        'ai_header': "AI Assistant Analysis",
        'reeng_header': "Re-engineering Proposals (TO-BE Model)",
        'export_header': "Export Data",
        'btn_pdf': "Download PDF Report",
        'btn_bpmn': "Download Corrected BPMN",
        'verify_header': "Verify Inserted Parameters",
        'eps_label': "EPS Score",
        'eri_label': "ERI Index",
        'eps_help': "Ethical Process Score: Global compliance level. 1.00 is maximum.",
        'eri_help': "Ethical Risk Index: Ratio between violations and maximum potential risk.",
        'rule_prefix': "Rule",
        'rules': {
            1: "R1: Privacy", 2: "R2: Supervision", 3: "R3: Equity", 4: "R4: Conflict",
            5: "R5: Anomaly", 6: "R6: Neutrality", 7: "R7: Responsibility",
            8: "R8: Appeal", 9: "R9: Transparency",
            10: "R10: Well-being", 11: "R11: Proportionality", 12: "R12: Disconnection"
        }
    }
}

T = translations[st.session_state.lang]

st.markdown("""
    <style>
        .violation-error { background-color: rgba(255, 75, 75, 0.15); border-left: 5px solid #FF4B4B; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-warning { background-color: rgba(255, 140, 0, 0.15); border-left: 5px solid #FF8C00; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-suggestion { background-color: rgba(255, 204, 128, 0.25); border-left: 5px solid #FFCC80; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        .violation-info { background-color: rgba(255, 255, 0, 0.15); border-left: 5px solid #FFFF00; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    is_lang_disabled = st.session_state.stage != 'upload'
    if st.button(T['lang_btn'], disabled=is_lang_disabled):
        st.session_state.lang = 'ENG' if st.session_state.lang == 'ITA' else 'ITA'
        st.rerun()

st.title(T['title'])
st.markdown(T['subtitle'])

with st.sidebar:
    st.header(T['sidebar_header'])
    uploaded_file = st.file_uploader(T['upload_label'], type="bpmn")

    custom_focus = st.text_area(
        label=T['focus_label'], 
        placeholder=T['focus_ph'],
        help=T['focus_help']
    )

    is_btn_disabled = (st.session_state.stage != 'upload') or (uploaded_file is None)
    process_button = st.button(T['btn_start'], use_container_width=True, disabled=is_btn_disabled)
    
    if st.session_state.stage != 'upload':
        if st.button(T['btn_new'], use_container_width=True):
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
    st.subheader(T['sub_rev'])
    
    with st.form(key="validation_form"):
        st.markdown(f"### {T['audit_sel']}")
        st.caption(T['audit_cap'])
        
        active_rules = []
        r_cols = st.columns(4)
        for i, (r_id, r_name) in enumerate(T['rules'].items()):
            if r_cols[i % 4].checkbox(r_name, value=True, key=f"chk_rule_{r_id}"):
                active_rules.append(r_id)
    
        for node in st.session_state.nodes:
            if hasattr(node, 'profile') and node.profile:
                st.markdown(f"### {T['element']}: `{node.name or node.id}`")
                st.caption(f"BPMN Type: {node.type_node}")
                
                b1, b2, b3, b4 = st.columns(4)
                node.profile.is_automated = b1.checkbox(T['node_auto'], value=node.profile.is_automated, key=f"a_{node.id}")
                node.profile.critical_task = b2.checkbox(T['node_crit'], value=node.profile.critical_task, key=f"c_{node.id}")
                node.profile.sensitive_data = b3.checkbox(T['node_sens'], value=node.profile.sensitive_data, key=f"s_{node.id}")
                node.profile.criteria_defined = b4.checkbox(T['node_def'], value=node.profile.criteria_defined, key=f"cd_{node.id}")
                
                node.profile.impacts_wellbeing = b1.checkbox(T['node_well'], value=node.profile.impacts_wellbeing, key=f"w_{node.id}")
                node.profile.outside_working_hours = b2.checkbox(T['node_off'], value=node.profile.outside_working_hours, key=f"o_{node.id}")
                node.profile.default_action = b3.checkbox(T['node_da'], value=node.profile.default_action, key=f"da_{node.id}")
                has_acc = b4.checkbox(T['node_acc'], value=bool(node.profile.acc_owner), key=f"h_acc_{node.id}")

                d1, d2 = st.columns(2)
                node.profile.type = d1.selectbox(T['node_type'], ["Decision", "Assignment", "Execution", "Communication", "Evaluation"], index=2, key=f"t_{node.id}")
                eq_options = [e.name for e in EquityAction]
                current_eq_name = node.profile.equity_action.name if hasattr(node.profile.equity_action, 'name') else "NONE"
                selected_eq = d2.selectbox(T['equity_label'], eq_options, index=eq_options.index(current_eq_name) if current_eq_name in eq_options else 0, key=f"eq_{node.id}")
                node.profile.equity_action = EquityAction[selected_eq]

                i1, i2 = st.columns(2)
                node.profile.actor = i1.text_input(T['node_act'], value=node.profile.actor or "", key=f"act_{node.id}")
                node.profile.beneficiary = i2.text_input(T['node_ben'], value=node.profile.beneficiary or "", key=f"ben_{node.id}")

                equity_options = ["NULL", "HEALTH_RECOVERY", "CAREGIVING", "DISABILITY_SUPPORT"]
                current_index = 0
                if node.profile.equity_note in equity_options:
                    current_index = equity_options.index(node.profile.equity_note)
                
                node.profile.equity_note = st.selectbox(T['node_eqn'], options=equity_options, index=current_index, key=f"eqn_{node.id}")
                st.markdown("---")
        
        submitted = st.form_submit_button(T['btn_audit'], use_container_width=True)
    
    if submitted:
        engine = EthicRuleEngine(st.session_state.nodes)
        ai_assistant = AIAssistant()
        violations = engine.run_all_rules(
        active_rules=active_rules, 
        lang=st.session_state.lang 
        )
        
        reengineering = ai_assistant.generate_reengineering_proposals(
            st.session_state.nodes, 
            violations, 
            custom_focus=custom_focus, 
            active_rules=active_rules,
            lang=st.session_state.lang
        )

        st.session_state.analysis_data = {
            'nodes': st.session_state.nodes,
            'violations': violations,
            'metrics': engine.calculate_eps_metrics(),
            'ai_feedback': ai_assistant.analyze_process_semantics(
                st.session_state.nodes, 
                custom_focus=custom_focus, 
                active_rules=active_rules,
                lang=st.session_state.lang
            ),
            'reengineering': reengineering
        }
        st.session_state.stage = 'dashboard'
        st.rerun()

elif st.session_state.stage == 'dashboard' and st.session_state.analysis_data:
    
    js_scroll = """
    <script>
        setTimeout(function() {
            var mainContainer = window.parent.document.querySelector('[data-testid="stMain"]');
            if (mainContainer) {
                mainContainer.scrollTo({top: 0, behavior: 'smooth'});
            } else {
                window.parent.scrollTo({top: 0, behavior: 'smooth'});
            }
        }, 100);
    </script>
    """
    st.components.v1.html(js_scroll, height=0)

    data = st.session_state.analysis_data
    if not os.path.exists("temp_process.bpmn") and st.session_state.bpmn_xml_raw:
        with open("temp_process.bpmn", "w", encoding="utf-8") as f:
            f.write(st.session_state.bpmn_xml_raw) 

    st.success(T['success'])
    col1, col2, col3 = st.columns(3)
    col1.metric(T['eps_label'], f"{data['metrics']['eps']:.2f}", help=T['eps_help'])
    col2.metric(T['eri_label'], f"{data['metrics']['eri']:.2f}", help=T['eri_help'])
    col3.metric(T['viol_detail'], len(data['violations']), help=T['viol_help'])

    st.divider()
    visualizza_bpmn_interattivo(st.session_state.bpmn_xml_raw, data['violations'])
    
    st.divider()
    st.subheader(T['viol_detail'])

    v_map = {}
    for v in data['violations']:
        v_map.setdefault(v.target_node, []).append(v)

    if not v_map:
        st.success(T['no_viol'])
    else:
        for t_id, v_list in v_map.items():
            node = next((n for n in data['nodes'] if n.id == t_id), None)
            t_name = node.name if node and node.name else t_id
            with st.expander(f"{T['element']}: {t_name}"):
                for v in v_list:
                    lvl = v.level.name.upper()
                    style_class = "violation-error" if lvl == "ERROR" else "violation-warning" if lvl == "WARNING" else "violation-suggestion" if lvl == "SUGGESTION" else "violation-info"
                    
                    r_name_translated = T['rules'].get(v.rule_number, v.rule_name)
                    display_name = r_name_translated.split(": ")[-1] if ": " in r_name_translated else r_name_translated
                    
                    st.markdown(f"""
                        <div class="{style_class}">
                            <b>{T['rule_prefix']} {v.rule_number}: {display_name}</b><br>
                            <small>{v.message}</small>
                        </div>
                    """, unsafe_allow_html=True)

    st.divider()
    cl, cr = st.columns([3, 1])
    with cl:
        st.subheader(T['ai_header'])
        st.info(data['ai_feedback'])
        st.subheader(T['reeng_header'])
        st.success(data.get('reengineering', "N/A"))

    with cr:
        st.subheader(T['export_header'])
        reeng_text = data.get('reengineering', "N/A")
        PDFReportGenerator.generate_pdf(data['violations'], data['ai_feedback'], data['metrics'], data['nodes'], reeng_text, "report_audit.pdf", lang=st.session_state.lang)
        with open("report_audit.pdf", "rb") as f:
            st.download_button(T['btn_pdf'], f, "Analisi_Etica_EthicBPMN.pdf", use_container_width=True)
        
        BpmnAutoFixer.generate_fixed_bpmn("temp_process.bpmn", data['nodes'], "Corrected_process.bpmn")
        with open("Corrected_process.bpmn", "rb") as f:
            st.download_button(T['btn_bpmn'], f, "Corrected_process.bpmn", use_container_width=True)

    st.divider()
    with st.expander(T['verify_header'], expanded=False):
        for node in data['nodes']:
            if node.profile:
                st.markdown(f"#### {T['element']}: `{node.name or node.id}`")
                v1, v2 = st.columns(2)
                v1.write(f"**{T['node_act']}:** {node.profile.actor or 'N/A'} | **{T['node_ben']}:** {node.profile.beneficiary or 'N/A'}")
                v2.write(f"**{T['node_type']}:** {node.profile.type} | **{T['equity_label']}:** {node.profile.equity_action.name}")