# src/rule_engine.py
from src.models import BpmnNode, Violation, RuleLevel, EquityAction

class EthicRuleEngine:
    def __init__(self, nodes: list[BpmnNode]):
        self.nodes = {node.id: node for node in nodes}
        self.violations = []

    def run_all_rules(self, active_rules=None) -> list[Violation]:
        """Esegue le regole etiche del framework EthicBPMN filtrate per scope."""
        # Salviamo le regole attive per usarle anche nel calcolo matematico. 
        # Se non viene passato nulla (es. file di test), le teniamo attive tutte e 12.
        self.active_rules = active_rules if active_rules is not None else list(range(1, 13))

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
            if not has_consent:
                self._add_violation(1, "Privacy e Minimizzazione", RuleLevel.ERROR, node.id, 
                                    "Il task tratta dati sensibili ma manca un flusso di 'Acquisizione Consenso Informato'.")

    def _check_rule_2_supervisione(self, node: BpmnNode):
        if node.profile.is_automated and node.profile.critical_task:
            has_human_override = False
            for next_id in node.outgoing_flows:
                next_node = self.nodes.get(next_id)
                if next_node and next_node.type_node == 'bpmn:userTask':
                    has_human_override = True
            
            if not has_human_override:
                self._add_violation(2, "Supervisione Umana", RuleLevel.ERROR, node.id, 
                                    "L'algoritmo prende una decisione critica senza la validazione obbligatoria di un operatore umano.")

    def _check_rule_3_equita(self, node: BpmnNode):
        if node.profile.sensitive_data and node.profile.is_automated:
            if "blind" not in node.name.lower() and "anonimo" not in node.name.lower():
                self._add_violation(3, "Equità e Antidiscriminazione", RuleLevel.ERROR, node.id, 
                                    "Dati sensibili elaborati da un algoritmo senza evidenza di 'Blind Processing'.")

    def _check_rule_4_conflitto_interessi(self, node: BpmnNode):
        if node.profile.type in ["Decision", "Evaluation"]:
            act = str(node.profile.actor).strip().lower() if node.profile.actor else ""
            
            if node.profile.beneficiary:
                beneficiaries_list = [b.strip().lower() for b in str(node.profile.beneficiary).split(',')]
                if act and act in beneficiaries_list:
                    self._add_violation(4, "Prevenzione del Conflitto di Interessi", RuleLevel.ERROR,  node.id, 
                        f"L'attore ({node.profile.actor}) è incluso tra i beneficiari della valutazione. "
                        f"L'imparzialità è compromessa."
                    )

    # REGOLE ALTE
    def _check_rule_5_contestualizzazione_anomalia(self, node: BpmnNode):
        if node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower()):
            has_investigation = any(n.type_node == 'bpmn:userTask' for n_id in node.outgoing_flows if (n := self.nodes.get(n_id)))
            if not has_investigation:
                self._add_violation(5, "Contestualizzazione Anomalia", RuleLevel.WARNING, node.id, 
                                    "L'anomalia di performance sfocia in una decisione automatica senza controllo investigativo.")

    def _check_rule_6_neutralita_diritti(self, node: BpmnNode):
        if node.profile.equity_action != EquityAction.NONE:
            self._add_violation(6, "Neutralità dei Diritti", RuleLevel.WARNING, node.id, 
                                "Logica di equità applicata. Assicurarsi che i report KPI siano normalizzati.")

    def _check_rule_7_responsabilita(self, node: BpmnNode):
        if node.profile.critical_task:
            if not node.profile.acc_owner or node.profile.acc_owner.lower() == "null":
                self._add_violation(7, "Responsabilità Identificata", RuleLevel.WARNING, node.id, 
                                    "Azione ad alto rischio senza un titolare umano associato.")

    # REGOLE MEDIE
    def _check_rule_8_appello(self, node: BpmnNode):
        if node.profile.critical_task and ("scart" in node.name.lower() or "rifiut" in node.name.lower()):
            has_catch_event = any(n.type_node == 'bpmn:intermediateCatchEvent' for n in self.nodes.values())
            if not has_catch_event:
                self._add_violation(8, "Reversibilità e Appello", RuleLevel.INFO, node.id, 
                                    "Decisione sfavorevole priva di una finestra di ricorso per l'utente.")

    def _check_rule_9_trasparenza(self, node: BpmnNode):
        if node.profile.critical_task and not node.profile.criteria_defined:
            self._add_violation(9, "Trasparenza e Spiegabilità", RuleLevel.INFO, node.id, 
                                "Punto decisionale opaco: i criteri non sono esplicitati.")

    # REGOLE BASSE
    def _check_rule_10_benessere(self, node: BpmnNode):
        if node.profile.impacts_wellbeing:
            has_rest = any("riposo" in n.name.lower() or "pausa" in n.name.lower() for n in self.nodes.values())
            if not has_rest:
                self._add_violation(10, "Beneficenza e Benessere", RuleLevel.SUGGESTION, node.id, 
                                    "Task ad alto impatto cognitivo. Si suggerisce di inserire pause.")

    def _check_rule_11_proporzionalita(self, node: BpmnNode):
        if node.profile.type == "Monitoring" or "report" in node.name.lower():
            self._add_violation(11, "Proporzionalità dello Sforzo", RuleLevel.SUGGESTION, node.id, 
                                "Task di monitoraggio. Verificare onerosità rispetto all'attività operativa.")

    def _check_rule_12_disconnessione(self, node: BpmnNode):
        if node.profile.outside_working_hours:
            self._add_violation(12, "Diritto alla Disconnessione", RuleLevel.SUGGESTION, node.id, 
                                "Task eseguito fuori orario. Usare TimerEvent per gestire la notifica nel turno successivo.")


    def _add_violation(self, r_num: int, r_name: str, level: RuleLevel, target_id: str, msg: str):
        node = self.nodes.get(target_id)
        node_display = node.name if node and node.name else target_id
        
        # Inseriamo il nome nel messaggio per chiarezza
        # full_message = f"[{node_display}] {msg}"
        
        self.violations.append(Violation(
            rule_number=r_num, 
            rule_name=r_name, 
            level=level, 
            target_node=target_id, 
            message=msg #full_message
            ))

    def calculate_eps_metrics(self) -> dict:
        """Calcola EPS e ERI basandosi solo sulle regole attive e sui trigger esatti."""
        r_max = 0
        r_obs = 0

        # Recuperiamo le regole attive
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
                
                # REGOLE MEDIE (Peso 2)
                if 8 in active_rules and node.profile.critical_task and ("scart" in node.name.lower() or "rifiut" in node.name.lower()): r_max += 2
                if 9 in active_rules and node.profile.critical_task: r_max += 2
                
                # REGOLE BASSE (Peso 1)
                if 10 in active_rules and node.profile.impacts_wellbeing: r_max += 1
                if 11 in active_rules and (node.profile.type == "Monitoring" or "report" in node.name.lower()): r_max += 1
                if 12 in active_rules and node.profile.outside_working_hours: r_max += 1

        # 2. Calcolo del Rischio Osservato (R_obs) in base ai pesi delle violazioni
        for v in self.violations:
            if v.level == RuleLevel.ERROR:
                r_obs += 4     
            elif v.level == RuleLevel.WARNING:
                r_obs += 3     
            elif v.level == RuleLevel.INFO:
                r_obs += 2     
            elif v.level == RuleLevel.SUGGESTION:
                r_obs += 1     

        # 3. Formule di Normalizzazione ERI e EPS
        eri = (r_obs / r_max) if r_max > 0 else 0.0
        eps = 1.0 - eri

        return {
            "r_max": r_max,
            "r_obs": r_obs,
            "eri": round(eri, 2),
            "eps": round(eps, 2)
        }