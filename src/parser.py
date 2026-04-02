# src/parser.py
import xml.etree.ElementTree as ET
from src.models import BpmnNode, TaskProfile

class BpmnParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        # I namespace standard dei file BPMN e la nostra estensione
        self.namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'ethic': 'http://ethicbpmn.org/schema/1.0/ethic'
        }

    def parse(self) -> list[BpmnNode]:
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        nodes = []

        # Tipi di nodi che vogliamo analizzare <-- ne ho aggiunti alcuni per coprire più casi reali
        target_tags = ['bpmn:task', 'bpmn:serviceTask', 'bpmn:userTask', 'bpmn:sendTask', 'bpmn:exclusiveGateway', 'bpmn:businessRuleTask']

        for process in root.findall('bpmn:process', self.namespaces):
            # Mappatura delle frecce (Sequence Flows)
            flows = {}
            for flow in process.findall('bpmn:sequenceFlow', self.namespaces):
                source = flow.get('sourceRef')
                target = flow.get('targetRef')
                if source not in flows:
                    flows[source] = []
                flows[source].append(target)

            # Estrazione dei Nodi
            for tag in target_tags:
                for elem in process.findall(tag, self.namespaces):
                    node_id = elem.get('id')
                    node_name = elem.get('name', 'Unnamed_Node')
                    
                    # Simuliamo la lettura dell'estensione EthicBPMN (se presente)
                    # Nella realtà, qui si scansiona <bpmn:extensionElements>
                    profile = self._extract_ethic_profile(elem)

                    nodes.append(BpmnNode(
                        id=node_id,
                        name=node_name,
                        type_node=tag,
                        profile=profile,
                        outgoing_flows=flows.get(node_id, [])
                    ))
        return nodes

    def _extract_ethic_profile(self, elem: ET.Element) -> TaskProfile | None:
        """
        Legge i parametri etici dal tag <ethic:TaskProfile> nascosto dentro <bpmn:extensionElements>.
        """
        # Cerca il blocco delle estensioni
        ext_elements = elem.find('bpmn:extensionElements', self.namespaces)
        if ext_elements is None:
            return None
            
        # Cerca il nostro tag specifico
        ethic_tag = ext_elements.find('ethic:TaskProfile', self.namespaces)
        if ethic_tag is None:
            return None

        # Helper per convertire le stringhe "true"/"false" di XML in booleani Python
        def str_to_bool(val):
            return str(val).lower() == 'true'

        try:
            # Crea e popola l'oggetto TaskProfile con i dati veri dell'XML!
            return TaskProfile(
                type=ethic_tag.get('type', 'Execution'),
                actor=ethic_tag.get('actor', 'System'),
                is_automated=str_to_bool(ethic_tag.get('is_automated')),
                acc_owner=ethic_tag.get('acc_owner'),
                critical_task=str_to_bool(ethic_tag.get('critical_task')),
                sensitive_data=str_to_bool(ethic_tag.get('sensitive_data')),
                equity_action=ethic_tag.get('equity_action', 'None'),
                equity_note=ethic_tag.get('equity_note'),
                criteria_defined=str_to_bool(ethic_tag.get('criteria_defined')),
                impacts_wellbeing=str_to_bool(ethic_tag.get('impacts_wellbeing')),
                outside_working_hours=str_to_bool(ethic_tag.get('outside_working_hours')),
                default_action=str_to_bool(ethic_tag.get('default_action'))
            )
        except Exception as e:
            print(f"Errore nel parsing del TaskProfile per il nodo {elem.get('name')}: {e}")
            return None