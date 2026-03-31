# src/rule_engine.py
from src.models import BpmnNode, Violation, RuleLevel

class EthicRuleEngine:
    def __init__(self, nodes: list[BpmnNode]):
        self.nodes = {node.id: node for node in nodes} # Dizionario per ricerca veloce
        self.violations = []

    def run_all_rules(self) -> list[Violation]:
        self.check_rule_2_supervisione()
        self.check_rule_6_accountability()
        self.check_rule_11_disconnessione()
        return self.violations

    def check_rule_2_supervisione(self):
        """Regola 2: Is_Automated + Critical_Task -> ERROR se manca UserTask a valle"""
        for node_id, node in self.nodes.items():
            if node.profile and node.profile.is_automated and node.profile.critical_task:
                has_human_override = False
                
                # Controllo i nodi successivi seguendo le frecce
                for next_id in node.outgoing_flows:
                    next_node = self.nodes.get(next_id)
                    if next_node and next_node.type_node == 'bpmn:userTask':
                        has_human_override = True
                
                if not has_human_override:
                    self.violations.append(Violation(
                        rule_number=2, rule_name="Supervisione Umana", level=RuleLevel.ERROR, target_node=node.name,
                        message="Task critico automatico senza UserTask (umano) a supervisionare l'output."
                    ))

    def check_rule_6_accountability(self):
        """Regola 6: Critical_Task -> WARNING se Acc_Owner è vuoto"""
        for node_id, node in self.nodes.items():
            if node.profile and node.profile.critical_task:
                if not node.profile.acc_owner or node.profile.acc_owner.lower() == "null":
                    self.violations.append(Violation(
                        rule_number=6, rule_name="Responsabilità Identificata", level=RuleLevel.WARNING, target_node=node.name,
                        message="Il task è critico ma manca un Accountability Owner legale assegnato."
                    ))

    def check_rule_11_disconnessione(self):
        """Regola 11: Outside_Working_Hours -> SUGGESTION se invia email"""
        for node_id, node in self.nodes.items():
            if node.profile and node.profile.outside_working_hours and "sendTask" in node.type_node:
                self.violations.append(Violation(
                        rule_number=11, rule_name="Diritto alla Disconnessione", level=RuleLevel.SUGGESTION, target_node=node.name,
                        message="Questo task invia comunicazioni fuori orario. Valutare l'inserimento di un TimerEvent di blocco."
                ))