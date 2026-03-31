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

        # Tipi di nodi che vogliamo analizzare
        target_tags = ['bpmn:task', 'bpmn:serviceTask', 'bpmn:userTask', 'bpmn:sendTask', 'bpmn:exclusiveGateway']

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
        Questa funzione cerca il tag <ethic:TaskProfile> dentro il nodo.
        Per ora, creiamo un Mock se il nodo ha la parola 'AI' o 'Automatico' nel nome
        per poter testare il motore anche senza un XML pre-compilato.
        """
        name = elem.get('name', '').lower()
        if "automatico" in name or "ai" in name or "algoritmo" in name:
            return TaskProfile(
                is_automated=True, 
                critical_task=True, 
                acc_owner="Null",
                sensitive_data=True
            )
        elif "notifica" in name or "email" in name:
            return TaskProfile(outside_working_hours=True)
            
        return None