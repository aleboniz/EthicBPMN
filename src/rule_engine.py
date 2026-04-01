# src/rule_engine.py
from src.models import BpmnNode, Violation, RuleLevel, EquityAction

class EthicRuleEngine:
    def __init__(self, nodes: list[BpmnNode]):
        self.nodes = {node.id: node for node in nodes}
        self.violations = []

    def run_all_rules(self) -> list[Violation]:
        """Esegue le 11 regole etiche del framework EthicBPMN."""
        for node_id, node in self.nodes.items():
            if not node.profile:
                continue
            
            # --- LIVELLO 1: REGOLE CRITICHE (Error - Peso 4) ---
            self._check_rule_1_privacy(node)
            self._check_rule_2_supervisione(node)
            self._check_rule_3_equita(node)

            # --- LIVELLO 2: REGOLE ALTE (Warning - Peso 3) ---
            self._check_rule_4_contestualizzazione_anomalia(node)
            self._check_rule_5_neutralita_diritti(node)
            self._check_rule_6_responsabilita(node)

            # --- LIVELLO 3: REGOLE MEDIE (Info - Peso 2) ---
            self._check_rule_7_appello(node)
            self._check_rule_8_trasparenza(node)

            # --- LIVELLO 4: REGOLE BASSE (Suggestion - Peso 1) ---
            self._check_rule_9_benessere(node)
            self._check_rule_10_proporzionalita(node)
            self._check_rule_11_disconnessione(node)

        return self.violations

    # ==========================================
    # 🔴 REGOLE CRITICHE (ERROR)
    # ==========================================
    def _check_rule_1_privacy(self, node: BpmnNode):
        """Regola 1: Privacy e Minimizzazione dei Dati (Marker: Sensitive_Data)"""
        if node.profile.sensitive_data:
            # Verifica che vi sia stata l'acquisizione del consenso
            has_consent = any("consenso" in n.name.lower() or "consent" in n.name.lower() for n in self.nodes.values())
            if not has_consent:
                self._add_violation(1, "Privacy e Minimizzazione", RuleLevel.ERROR, node.name, 
                                    "Il task tratta dati sensibili ma manca un flusso di 'Acquisizione Consenso Informato' o di anonimizzazione a monte.")

    def _check_rule_2_supervisione(self, node: BpmnNode):
        """Regola 2: Supervisione Umana (Marker: Is_Automated + Critical_Task)"""
        if node.profile.is_automated and node.profile.critical_task:
            has_human_override = False
            for next_id in node.outgoing_flows:
                next_node = self.nodes.get(next_id)
                if next_node and next_node.type_node == 'bpmn:userTask':
                    has_human_override = True
            
            if not has_human_override:
                self._add_violation(2, "Supervisione Umana", RuleLevel.ERROR, node.name, 
                                    "L'algoritmo prende una decisione critica senza la validazione obbligatoria di un operatore umano (User Task) a valle.")

    def _check_rule_3_equita(self, node: BpmnNode):
        """Regola 3: Equità e Antidiscriminazione (Marker: Sensitive_Data in automatismi)"""
        if node.profile.sensitive_data and node.profile.is_automated:
            if "blind" not in node.name.lower() and "anonimo" not in node.name.lower():
                self._add_violation(3, "Equità e Antidiscriminazione", RuleLevel.ERROR, node.name, 
                                    "Dati sensibili elaborati da un algoritmo senza evidenza di 'Blind Processing' (anonimizzazione funzionale). Rischio di bias.")

    # ==========================================
    # 🟠 REGOLE ALTE (WARNING)
    # ==========================================
    def _check_rule_4_contestualizzazione_anomalia(self, node: BpmnNode):
        """Regola 4: Contestualizzazione dell'Anomalia (Marker: Trigger su Gateways)"""
        if node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower() or 'scarto' in node.name.lower()):
            has_investigation = any(n.type_node == 'bpmn:userTask' for n_id in node.outgoing_flows if (n := self.nodes.get(n_id)))
            if not has_investigation:
                self._add_violation(4, "Contestualizzazione Anomalia", RuleLevel.WARNING, node.name, 
                                    "L'anomalia di performance sfocia in una decisione automatica senza transitare per un task investigativo.")

    def _check_rule_5_neutralita_diritti(self, node: BpmnNode):
        """Regola 5: Neutralità dei Diritti (Marker: Equity_Action)"""
        if node.profile.equity_action != EquityAction.NONE:
            self._add_violation(5, "Neutralità dei Diritti", RuleLevel.WARNING, node.name, 
                                "Logica di equità applicata. Assicurarsi che i report di KPI (es. tempi, gap) siano normalizzati per non penalizzare il beneficiario visivamente.")

    def _check_rule_6_responsabilita(self, node: BpmnNode):
        """Regola 6: Responsabilità Chiaramente Identificata (Marker: Critical_Task)"""
        if node.profile.critical_task:
            if not node.profile.acc_owner or node.profile.acc_owner.lower() == "null":
                self._add_violation(6, "Responsabilità Identificata", RuleLevel.WARNING, node.name, 
                                    "Azione ad alto rischio senza un titolare umano associato (Acc_Owner assente).")

    # ==========================================
    # 🟡 REGOLE MEDIE (INFO)
    # ==========================================
    def _check_rule_7_appello(self, node: BpmnNode):
        """Regola 7: Reversibilità e Diritto di Appello (Marker: Critical_Task + esito)"""
        if node.profile.critical_task and ("scart" in node.name.lower() or "rifiut" in node.name.lower()):
            has_catch_event = any(n.type_node == 'bpmn:intermediateCatchEvent' for n in self.nodes.values())
            if not has_catch_event:
                self._add_violation(7, "Reversibilità e Appello", RuleLevel.INFO, node.name, 
                                    "Decisione sfavorevole priva di una finestra di ricorso (CatchEvent) per l'utente.")

    def _check_rule_8_trasparenza(self, node: BpmnNode):
        """Regola 8: Trasparenza e Spiegabilità (Marker: Critical_Task + Criteria_Defined == False)"""
        if node.profile.critical_task and not node.profile.criteria_defined:
            self._add_violation(8, "Trasparenza e Spiegabilità", RuleLevel.INFO, node.name, 
                                "Punto decisionale opaco: i criteri non sono esplicitati (Criteria_Defined = False). Necessario inviare notifica motivazionale.")

    # ==========================================
    # 🟢 REGOLE BASSE (SUGGESTION)
    # ==========================================
    def _check_rule_9_benessere(self, node: BpmnNode):
        """Regola 9: Beneficenza e Benessere (Marker: Impacts_Wellbeing)"""
        if node.profile.impacts_wellbeing:
            has_rest = any("riposo" in n.name.lower() or "pausa" in n.name.lower() for n in self.nodes.values())
            if not has_rest:
                self._add_violation(9, "Beneficenza e Benessere", RuleLevel.SUGGESTION, node.name, 
                                    "Task ad alto impatto cognitivo o gravoso. Si suggerisce di inserire gateway per la ridistribuzione del carico o riposo.")

    def _check_rule_10_proporzionalita(self, node: BpmnNode):
        """Regola 10: Proporzionalità dello Sforzo (Marker: Type)"""
        if node.profile.type == "Monitoring" or "report" in node.name.lower():
            self._add_violation(10, "Proporzionalità dello Sforzo", RuleLevel.SUGGESTION, node.name, 
                                "Task di reporting/monitoraggio. Assicurarsi che il controllo non sia più oneroso dell'attività operativa stessa.")

    def _check_rule_11_disconnessione(self, node: BpmnNode):
        """Regola 11: Diritto alla Disconnessione (Marker: Outside_Working_Hours)"""
        if node.profile.outside_working_hours:
            self._add_violation(11, "Diritto alla Disconnessione", RuleLevel.SUGGESTION, node.name, 
                                "Task eseguito fuori orario standard. Inserire un TimerEvent per trattenere la notifica/azione fino al turno successivo.")

    # ==========================================
    # HELPER E CALCOLO MATEMATICO
    # ==========================================
    def _add_violation(self, r_num: int, r_name: str, level: RuleLevel, target: str, msg: str):
        self.violations.append(Violation(rule_number=r_num, rule_name=r_name, level=level, target_node=target, message=msg))

    def calculate_eps_metrics(self) -> dict:
        """Calcola EPS e ERI basandosi su 4 pesi (CRITICA=4, ALTA=3, MEDIA=2, BASSA=1) per le 11 regole."""
        r_max = 0
        r_obs = 0

        # 1. Rischio Massimo (Pesi delle regole applicabili in base ai parametri)
        for node_id, node in self.nodes.items():
            if node.profile:
                # Regola 1 e 3 (Critiche - Peso 4)
                if node.profile.sensitive_data:
                    r_max += 8  # 4 + 4
                # Regola 2 (Critica - Peso 4)
                if node.profile.is_automated and node.profile.critical_task:
                    r_max += 4
                # Regola 4 (Alta - Peso 3)
                if node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower()):
                    r_max += 3
                # Regola 5 (Alta - Peso 3)
                if node.profile.equity_action != EquityAction.NONE:
                    r_max += 3
                # Regola 6, 7, 8 (Alta=3, Media=2, Media=2) applicabili a Critical Tasks
                if node.profile.critical_task:
                    r_max += 7  # 3 + 2 + 2
                # Regola 9 (Bassa - Peso 1)
                if node.profile.impacts_wellbeing:
                    r_max += 1
                # Regola 10 (Bassa - Peso 1) si applica sempre per la proporzionalità globale
                r_max += 1
                # Regola 11 (Bassa - Peso 1)
                if node.profile.outside_working_hours:
                    r_max += 1

        # 2. Rischio Osservato (Somma delle violazioni reali)
        for v in self.violations:
            if v.level == RuleLevel.ERROR:
                r_obs += 4     # Regole Critiche
            elif v.level == RuleLevel.WARNING:
                r_obs += 3     # Regole Alte
            elif v.level == RuleLevel.INFO:
                r_obs += 2     # Regole Medie
            elif v.level == RuleLevel.SUGGESTION:
                r_obs += 1     # Regole Basse

        # 3. Calcolo Indici
        eri = (r_obs / r_max) if r_max > 0 else 0.0
        eps = 1.0 - eri

        return {
            "r_max": r_max,
            "r_obs": r_obs,
            "eri": round(eri, 2),
            "eps": round(eps, 2)
        }