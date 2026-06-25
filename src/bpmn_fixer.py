import xml.etree.ElementTree as ET
from src.models import BpmnNode, EquityAction

class BpmnAutoFixer:
    @staticmethod
    def generate_fixed_bpmn(original_file_path: str, nodes: list[BpmnNode], output_path: str = "fixed_process.bpmn"):
        # Registrazione namespace originali
        ET.register_namespace('bpmn', 'http://www.omg.org/spec/BPMN/20100524/MODEL')
        ET.register_namespace('bpmndi', 'http://www.omg.org/spec/BPMN/20100524/DI')
        ET.register_namespace('dc', 'http://www.omg.org/spec/DD/20100524/DC')
        ET.register_namespace('di', 'http://www.omg.org/spec/DD/20100524/DI')
        ET.register_namespace('ethic', 'http://ethicbpmn.org/schema/1.0/ethic')

        tree = ET.parse(original_file_path)
        root = tree.getroot()
        namespaces = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

        node_dict = {n.id: n for n in nodes}

        # Analisi XML
        for process in root.findall('bpmn:process', namespaces):
            for elem in process:
                node_id = elem.get('id')
                if node_id in node_dict:
                    node = node_dict[node_id]
                    if node.profile:
                        if node.profile.critical_task and (not node.profile.acc_owner or node.profile.acc_owner.lower() == "null"):
                            node.profile.acc_owner = "Compliance_Officer"
                        
                        if node.profile.outside_working_hours:
                            node.profile.outside_working_hours = False
                            
                        if node.profile.equity_action != EquityAction.NONE:
                            node.profile.criteria_defined = True

                        ext_elem = elem.find('bpmn:extensionElements', namespaces)
                        if ext_elem is None:
                            ext_elem = ET.Element('{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements')
                            elem.insert(0, ext_elem)

                        old_profile = ext_elem.find('{http://ethicbpmn.org/schema/1.0/ethic}TaskProfile')
                        if old_profile is not None:
                            ext_elem.remove(old_profile)

                        attrs = {
                            'type': str(node.profile.type or "Execution"),
                            'actor': str(node.profile.actor or ""),
                            'is_automated': str(node.profile.is_automated).lower(),
                            'critical_task': str(node.profile.critical_task).lower(),
                            'sensitive_data': str(node.profile.sensitive_data).lower(),
                            'equity_action': str(node.profile.equity_action.name),
                            'criteria_defined': str(node.profile.criteria_defined).lower(),
                            'impacts_wellbeing': str(node.profile.impacts_wellbeing).lower(),
                            'outside_working_hours': str(node.profile.outside_working_hours).lower(),
                            'default_action': str(node.profile.default_action).lower() # ORA PRESENTE!
                        }

                        if node.profile.acc_owner and str(node.profile.acc_owner).lower() not in ["null", "none", ""]:
                            attrs['acc_owner'] = str(node.profile.acc_owner)
                            
                        if node.profile.equity_note and str(node.profile.equity_note).upper() != "NULL":
                            attrs['equity_note'] = str(node.profile.equity_note)
                            
                        if node.profile.beneficiary:
                            if isinstance(node.profile.beneficiary, list):
                                attrs['beneficiary'] = ",".join(node.profile.beneficiary)
                            else:
                                attrs['beneficiary'] = str(node.profile.beneficiary)

                        # Crezione tag XML con i parametri corretti
                        new_profile = ET.Element('{http://ethicbpmn.org/schema/1.0/ethic}TaskProfile', attrs)
                        ext_elem.append(new_profile)

        # Salva nuovo file
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return output_path