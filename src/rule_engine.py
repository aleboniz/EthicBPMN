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
            
            # LIVELLO 1: REGOLE CRITICHE
            self._check_rule_1_privacy(node)
            self._check_rule_2_supervisione(node)
            self._check_rule_3_equita(node)

            # LIVELLO 2: REGOLE ALTE
            self._check_rule_4_contestualizzazione_anomalia(node)
            self._check_rule_5_neutralita_diritti(node)
            self._check_rule_6_responsabilita(node)

            # LIVELLO 3: REGOLE MEDIE
            self._check_rule_7_appello(node)
            self._check_rule_8_trasparenza(node)

            # LIVELLO 4: REGOLE BASSE 
            self._check_rule_9_benessere(node)
            self._check_rule_10_proporzionalita(node)
            self._check_rule_11_disconnessione(node)

        return self.violations

    # REGOLE CRITICHE
    def _check_rule_1_privacy(self, node: BpmnNode):
        if node.profile.sensitive_data:
            has_consent = any("consenso" in n.name.lower() or "consent" in n.name.lower() for n in self.nodes.values())
            if not has_consent:
                # CAMBIATO: node.id invece di node.name
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
                # CAMBIATO: node.id
                self._add_violation(2, "Supervisione Umana", RuleLevel.ERROR, node.id, 
                                    "L'algoritmo prende una decisione critica senza la validazione obbligatoria di un operatore umano.")

    def _check_rule_3_equita(self, node: BpmnNode):
        if node.profile.sensitive_data and node.profile.is_automated:
            if "blind" not in node.name.lower() and "anonimo" not in node.name.lower():
                # CAMBIATO: node.id
                self._add_violation(3, "Equità e Antidiscriminazione", RuleLevel.ERROR, node.id, 
                                    "Dati sensibili elaborati da un algoritmo senza evidenza di 'Blind Processing'.")

    # REGOLE ALTE
    def _check_rule_4_contestualizzazione_anomalia(self, node: BpmnNode):
        if node.type_node in ['bpmn:exclusiveGateway', 'bpmn:boundaryEvent'] and ('anomali' in node.name.lower() or 'performance' in node.name.lower()):
            has_investigation = any(n.type_node == 'bpmn:userTask' for n_id in node.outgoing_flows if (n := self.nodes.get(n_id)))
            if not has_investigation:
                self._add_violation(4, "Contestualizzazione Anomalia", RuleLevel.WARNING, node.id, 
                                    "L'anomalia di performance sfocia in una decisione automatica senza controllo investigativo.")

    def _check_rule_5_neutralita_diritti(self, node: BpmnNode):
        if node.profile.equity_action != EquityAction.NONE:
            self._add_violation(5, "Neutralità dei Diritti", RuleLevel.WARNING, node.id, 
                                "Logica di equità applicata. Assicurarsi che i report KPI siano normalizzati.")

    def _check_rule_6_responsabilita(self, node: BpmnNode):
        if node.profile.critical_task:
            if not node.profile.acc_owner or node.profile.acc_owner.lower() == "null":
                self._add_violation(6, "Responsabilità Identificata", RuleLevel.WARNING, node.id, 
                                    "Azione ad alto rischio senza un titolare umano associato.")

    # REGOLE MEDIE
    def _check_rule_7_appello(self, node: BpmnNode):
        if node.profile.critical_task and ("scart" in node.name.lower() or "rifiut" in node.name.lower()):
            has_catch_event = any(n.type_node == 'bpmn:intermediateCatchEvent' for n in self.nodes.values())
            if not has_catch_event:
                self._add_violation(7, "Reversibilità e Appello", RuleLevel.INFO, node.id, 
                                    "Decisione sfavorevole priva di una finestra di ricorso per l'utente.")

    def _check_rule_8_trasparenza(self, node: BpmnNode):
        if node.profile.critical_task and not node.profile.criteria_defined:
            self._add_violation(8, "Trasparenza e Spiegabilità", RuleLevel.INFO, node.id, 
                                "Punto decisionale opaco: i criteri non sono esplicitati.")

    # REGOLE BASSE
    def _check_rule_9_benessere(self, node: BpmnNode):
        if node.profile.impacts_wellbeing:
            has_rest = any("riposo" in n.name.lower() or "pausa" in n.name.lower() for n in self.nodes.values())
            if not has_rest:
                self._add_violation(9, "Beneficenza e Benessere", RuleLevel.SUGGESTION, node.id, 
                                    "Task ad alto impatto cognitivo. Si suggerisce di inserire pause.")

    def _check_rule_10_proporzionalita(self, node: BpmnNode):
        if node.profile.type == "Monitoring" or "report" in node.name.lower():
            self._add_violation(10, "Proporzionalità dello Sforzo", RuleLevel.SUGGESTION, node.id, 
                                "Task di monitoraggio. Verificare onerosità rispetto all'attività operativa.")

    def _check_rule_11_disconnessione(self, node: BpmnNode):
        if node.profile.outside_working_hours:
            self._add_violation(11, "Diritto alla Disconnessione", RuleLevel.SUGGESTION, node.id, 
                                "Task eseguito fuori orario. Usare TimerEvent per gestire la notifica nel turno successivo.")


    def _add_violation(self, r_num: int, r_name: str, level: RuleLevel, target_id: str, msg: str):
        self.violations.append(Violation(
            rule_number=r_num, 
            rule_name=r_name, 
            level=level, 
            target_node=target_id, 
            message=msg
        ))

    def calculate_eps_metrics(self) -> dict:
        """Calcola EPS e ERI basandosi su 4 pesi (CRITICA=4, ALTA=3, MEDIA=2, BASSA=1) per le 11 regole."""
        r_max = 0
        r_obs = 0

        # 1. Rischio Massimo
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