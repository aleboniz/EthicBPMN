# src/parser.py
import xml.etree.ElementTree as ET
from src.models import BpmnNode, TaskProfile

class BpmnParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'ethic': 'http://ethicbpmn.org/schema/1.0/ethic'
        }

    def parse(self) -> list[BpmnNode]:
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        nodes = []

        org_map = {}
        
        # 1. Estrazione Pool 
        collaboration = root.find('bpmn:collaboration', self.namespaces)
        pool_process_map = {}
        if collaboration is not None:
            for participant in collaboration.findall('bpmn:participant', self.namespaces):
                p_id = participant.get('processRef')
                p_name = participant.get('name')
                if p_id:
                    pool_process_map[p_id] = p_name

        # 2. Estrazione Lane 
        for process in root.findall('bpmn:process', self.namespaces):
            proc_id = process.get('id')
            pool_name = pool_process_map.get(proc_id)
            
            lane_set = process.find('bpmn:laneSet', self.namespaces)
            if lane_set is not None:
                for lane in lane_set.findall('bpmn:lane', self.namespaces):
                    lane_name = lane.get('name')
                    
                    for ref in lane.findall('bpmn:flowNodeRef', self.namespaces):
                        node_ref = ref.text.strip() if ref.text else None
                        if node_ref:
                            org_map[node_ref] = {
                                "pool": pool_name,
                                "lane": lane_name
                            }

        target_tags = [
            'bpmn:task', 'bpmn:serviceTask', 'bpmn:userTask', 
            'bpmn:sendTask', 'bpmn:businessRuleTask', 'bpmn:receiveTask',
            'bpmn:exclusiveGateway', 'bpmn:parallelGateway', 'bpmn:inclusiveGateway',
            'bpmn:intermediateCatchEvent', 'bpmn:intermediateThrowEvent',
            'bpmn:boundaryEvent', 'bpmn:callActivity'
        ]

        for process in root.findall('bpmn:process', self.namespaces):
            flows = {}
            for flow in process.findall('bpmn:sequenceFlow', self.namespaces):
                source = flow.get('sourceRef')
                target = flow.get('targetRef')
                if source not in flows: flows[source] = []
                flows[source].append(target)

            for tag in target_tags:
                for elem in process.findall(tag, self.namespaces):
                    node_id = elem.get('id')
                    node_name = elem.get('name')
                    
                    if not node_name:
                        if tag == 'bpmn:intermediateCatchEvent': node_name = "Evento di Attesa"
                        elif tag == 'bpmn:boundaryEvent': node_name = "Evento di Eccezione"
                        elif 'Gateway' in tag: node_name = "Bivio Decisionale"
                        elif tag == 'bpmn:intermediateThrowEvent': node_name = "Evento di Invio"
                        else: node_name = node_id

                    profile = self._extract_ethic_profile(elem)
                    
                    org_info = org_map.get(node_id, {})

                    nodes.append(BpmnNode(
                        id=node_id,
                        name=node_name,
                        type_node=tag,
                        profile=profile,
                        outgoing_flows=flows.get(node_id, []),
                        pool=org_info.get("pool"),
                        lane=org_info.get("lane")  
                    ))
        return nodes

    def _extract_ethic_profile(self, elem: ET.Element) -> TaskProfile | None:
        ext_elements = elem.find('bpmn:extensionElements', self.namespaces)
        if ext_elements is None: return None
        ethic_tag = ext_elements.find('ethic:TaskProfile', self.namespaces)
        if ethic_tag is None: return None

        def str_to_bool(val): return str(val).lower() == 'true'

        try:
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
        except Exception:
            return None