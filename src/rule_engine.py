# src/rule_engine.py
from src.models import BpmnNode, Violation, RuleLevel, EquityAction

class EthicRuleEngine:
    def __init__(self, nodes: list[BpmnNode]):
        self.nodes = {node.id: node for node in nodes}
        self.violations = []

    def run_all_rules(self, active_rules=None, lang="ITA") -> list[Violation]:
        """Esegue le regole etiche del framework EthicBPMN filtrate per scope e lingua."""
        self.active_rules = active_rules if active_rules is not None else list(range(1, 13))
        self.lang = lang # Salviamo la lingua per i messaggi

        for node_id, node in self.nodes.items():
            if not node.profile:
                continue
            
            # LIVELLO 1: REGOLE CRITICHE
            if 1 in self.active_rules: self._check_rule_1_privacy(node)
            if 2 in self.active_rules: self._check_rule_2_supervisione(node)
            if 3 in self.active_rules: self._check_rule_3_equita(node)
            if 4 in self.active_rules: self._check_rule_4_conflitto_interessi(node)

            # LIVELLO 2: REGOLE ALTE
            if 5 in self.active_rules: self._check_rule_5_contestualizzazione_anomalia(node)
            if 6 in self.active_rules: self._check_rule_6_neutralita_diritti(node)
            if 7 in self.active_rules: self._check_rule_7_responsabilita(node)

            # LIVELLO 3: REGOLE MEDIE
            if 8 in self.active_rules: self._check_rule_8_appello(node)
            if 9 in self.active_rules: self._check_rule_9_trasparenza(node)

            # LIVELLO 4: REGOLE BASSE 
            if 10 in self.active_rules: self._check_rule_10_benessere(node)
            if 11 in self.active_rules: self._check_rule_11_proporzionalita(node)
            if 12 in self.active_rules: self._check_rule_12_disconnessione(node)

        return self.violations

    # REGOLE CRITICHE
    def _check_rule_1_privacy(self, node: BpmnNode):
        if node.profile.sensitive_data:
            has_consent = any("consenso" in n.name.lower() or "consent" in n.name.lower() for n in self.nodes.values())
            if not has_consent and node.profile.equity_action != EquityAction.INFORMED_CONSENT:
                msg = ("Il task tratta dati sensibili ma manca un flusso di 'Acquisizione Consenso Informato'." if self.lang == "ITA" 
                       else "The task processes sensitive data but lacks an 'Informed Consent Acquisition' flow.")
                self._add_violation(1, "Privacy", RuleLevel.ERROR, node.id, msg)

    def _check_rule_2_supervisione(self, node: BpmnNode):
        if node.profile.is_automated and node.profile.critical_task:
            has_human_override = False
            for next_id in node.outgoing_flows:
                next_node = self.nodes.get(next_id)
                if next_node and next_node.type_node == 'bpmn:userTask':
                    has_human_override = True
            
            if not has_human_override and node.profile.equity_action != EquityAction.HUMAN_VALIDATION:
                msg = ("L'algoritmo prende una decisione critica senza la validazione obbligatoria di un operatore umano." if self.lang == "ITA" 
                       else "The algorithm makes a critical decision without the mandatory validation of a human operator.")
                self._add_violation(2, "Supervision", RuleLevel.ERROR, node.id, msg)

    def _check_rule_3_equita(self, node: BpmnNode):
        if node.profile.sensitive_data and node.profile.is_automated:
            if "blind" not in node.name.lower() and "anonimo" not in node.name.lower() and node.profile.equity_action != EquityAction.BLIND_PROCESSING:
                msg = ("Dati sensibili elaborati da un algoritmo senza evidenza di 'Blind Processing'." if self.lang == "ITA" 
                       else "Sensitive data processed by an algorithm without evidence of 'Blind Processing'.")
                self._add_violation(3, "Equity", RuleLevel.ERROR, node.id, msg)

    def _check_rule_4_conflitto_interessi(self, node: BpmnNode):
        if node.profile.type in ["Decision", "Evaluation"]:
            act = str(node.profile.actor).strip().lower() if node.profile.actor else ""
            if node.profile.beneficiary:
                beneficiaries_list = [b.strip().lower() for b in str(node.profile.beneficiary).split(',')]
                if act and act in beneficiaries_list:
                    msg = (f"L'attore ({node.profile.actor}) è incluso tra i beneficiari della valutazione. L'imparzialità è compromessa." if self.lang == "ITA" 
                           else f"The actor ({node.profile.actor}) is included among the beneficiaries of the evaluation. Impartiality is compromised.")
                    self._add_violation(4, "Conflict of Interest", RuleLevel.ERROR, node.id, msg)

    # REGOLE ALTE
    def _check_rule_5_contestualizzazione_anomalia(self, node: BpmnNode):
        if node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower()):
            has_investigation = any(n.type_node == 'bpmn:userTask' for n_id in node.outgoing_flows if (n := self.nodes.get(n_id)))
            if not has_investigation:
                msg = ("L'anomalia di performance sfocia in una decisione automatica senza controllo investigativo." if self.lang == "ITA" 
                       else "Performance anomaly leads to an automatic decision without investigative control.")
                self._add_violation(5, "Anomaly Context", RuleLevel.WARNING, node.id, msg)

    def _check_rule_6_neutralita_diritti(self, node: BpmnNode):
        current_action = str(node.profile.equity_action).strip()
        
        if '.' in current_action:
            current_action = current_action.split('.')[-1]
            
        azioni_positive_e_neutre = [
            "BLIND_PROCESSING", "HUMAN_VALIDATION", "CONTEXT_PROVIDED", 
            "RIGHT_TO_APPEAL", "TRANSPARENCY_LOG", "INFORMED_CONSENT", 
            "INDEPENDENT_REVIEW", "NONE"
        ]
        
        if current_action not in azioni_positive_e_neutre:
            msg = ("Logica di equità applicata. Assicurarsi che i report KPI siano normalizzati." if self.lang == "ITA" 
                   else "Equity logic applied. Ensure KPI reports are normalized.")
            self._add_violation(6, "Neutrality", RuleLevel.WARNING, node.id, msg)

    def _check_rule_7_responsabilita(self, node: BpmnNode):
        if node.profile.critical_task:
            if not node.profile.acc_owner or node.profile.acc_owner.lower() == "null":
                msg = ("Azione ad alto rischio senza un titolare umano associato." if self.lang == "ITA" 
                       else "High-risk action without an associated human owner.")
                self._add_violation(7, "Responsibility", RuleLevel.WARNING, node.id, msg)

    # REGOLE MEDIE
    def _check_rule_8_appello(self, node: BpmnNode):
        parole_chiave_negative = [
            "scart", "rifiut", "bocci", "negativ", "licenzi", 
            "tagli", "sanzion", "multa", "sospend", "sospens", "errore"
        ]
       
        if node.profile.critical_task and any(p in node.name.lower() for p in parole_chiave_negative):
            
            has_recourse_window = False
            visitati = set()
            
            def esplora_percorso(current_node: BpmnNode):
                nonlocal has_recourse_window
                if not current_node or current_node.id in visitati or has_recourse_window:
                    return
                visitati.add(current_node.id)
                
                for next_id in current_node.outgoing_flows:
                    next_node = self.nodes.get(next_id)
                    if next_node:
                        if next_node.type_node == 'bpmn:intermediateCatchEvent':
                            has_recourse_window = True
                            return
                        if next_node.type_node != 'bpmn:endEvent':
                            esplora_percorso(next_node)

            esplora_percorso(node)
            
            if not has_recourse_window:
                msg = ("Decisione sfavorevole priva di una finestra di ricorso." if self.lang == "ITA" 
                       else "Adverse decision lacking a recourse window on its specific termination path.")
                self._add_violation(8, "Appeal", RuleLevel.INFO, node.id, msg)

    def _check_rule_9_trasparenza(self, node: BpmnNode):
        if node.profile.critical_task and not node.profile.criteria_defined:
            msg = ("Punto decisionale opaco: i criteri non sono esplicitati." if self.lang == "ITA" 
                   else "Opaque decision point: criteria are not explicit.")
            self._add_violation(9, "Transparency", RuleLevel.INFO, node.id, msg)

    # REGOLE BASSE
    def _check_rule_10_benessere(self, node: BpmnNode):
        if node.profile.impacts_wellbeing:
            has_rest = any("riposo" in n.name.lower() or "pausa" in n.name.lower() for n in self.nodes.values())
            if not has_rest:
                msg = ("Task ad alto impatto cognitivo. Si suggerisce di inserire pause." if self.lang == "ITA" 
                       else "High cognitive impact task. It is suggested to insert breaks.")
                self._add_violation(10, "Well-being", RuleLevel.SUGGESTION, node.id, msg)

    def _check_rule_11_proporzionalita(self, node: BpmnNode):
        if node.profile.type == "Monitoring" or "report" in node.name.lower():
            msg = ("Task di monitoraggio. Verificare onerosità rispetto all'attività operativa." if self.lang == "ITA" 
                   else "Monitoring task. Verify burden relative to operational activity.")
            self._add_violation(11, "Proportionality", RuleLevel.SUGGESTION, node.id, msg)

    def _check_rule_12_disconnessione(self, node: BpmnNode):
        if node.profile.outside_working_hours:
            msg = ("Task eseguito fuori orario. Usare TimerEvent per gestire la notifica nel turno successivo." if self.lang == "ITA" 
                   else "Task executed off-hours. Use TimerEvent to manage notification in the next shift.")
            self._add_violation(12, "Disconnection", RuleLevel.SUGGESTION, node.id, msg)


    def _add_violation(self, r_num: int, r_name: str, level: RuleLevel, target_id: str, msg: str):
        self.violations.append(Violation(
            rule_number=r_num, 
            rule_name=r_name, 
            level=level, 
            target_node=target_id, 
            message=msg
            ))

    def calculate_eps_metrics(self) -> dict:
        r_max = 0
        r_obs = 0
        active_rules = getattr(self, 'active_rules', list(range(1, 13)))

        # 1. Calcolo del Serbatoio di Rischio Massimo (R_max) tarato al millimetro
        for node_id, node in self.nodes.items():
            if node.profile:
                # REGOLE CRITICHE (Peso 4)
                if 1 in active_rules and node.profile.sensitive_data: r_max += 4
                if 2 in active_rules and node.profile.is_automated and node.profile.critical_task: r_max += 4
                if 3 in active_rules and node.profile.sensitive_data and node.profile.is_automated: r_max += 4
                if 4 in active_rules and node.profile.type in ["Decision", "Evaluation"]: r_max += 4 
                # REGOLE ALTE (Peso 3)
                if 5 in active_rules and node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower()): r_max += 3
                if 6 in active_rules and node.profile.equity_action != EquityAction.NONE: r_max += 3
                if 7 in active_rules and node.profile.critical_task: r_max += 3
                # REGOLE ALTE (Peso 3)
                if 8 in active_rules and node.profile.critical_task and any(p in node.name.lower() for p in ["scart", "rifiut", "bocci", "negativ", "licenzi", "tagli", "sanzion", "multa", "sospend", "sospens", "errore"]): r_max += 2
                if 9 in active_rules and node.profile.critical_task: r_max += 2
                # REGOLE BASSE (Peso 1)
                if 10 in active_rules and node.profile.impacts_wellbeing: r_max += 1
                if 11 in active_rules and (node.profile.type == "Monitoring" or "report" in node.name.lower()): r_max += 1
                if 12 in active_rules and node.profile.outside_working_hours: r_max += 1

        # 2. Calcolo del Rischio Osservato (R_obs) in base ai pesi delle violazioni
        for v in self.violations:
            if v.level == RuleLevel.ERROR: r_obs += 4     
            elif v.level == RuleLevel.WARNING: r_obs += 3     
            elif v.level == RuleLevel.INFO: r_obs += 2     
            elif v.level == RuleLevel.SUGGESTION: r_obs += 1     

        # 3. Formule di Normalizzazione ERI e EPS
        eri = (r_obs / r_max) if r_max > 0 else 0.0
        eps = 1.0 - eri

        return {
            "r_max": r_max, "r_obs": r_obs,
            "eri": round(eri, 2), "eps": round(eps, 2)
        }

    
   