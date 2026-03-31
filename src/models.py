# src/models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class EquityAction(str, Enum):
    NONE = "None"
    GAP_NEUTRALIZATION = "Gap_Neutralization"
    SCORE_BOOSTING = "Score_Boosting"
    THRESHOLD_ADJUSTMENT = "Threshold_Adjustment"
    TIME_EXTENSION = "Time_Extension"
    ALTERNATIVE_ROUTING = "Alternative_Routing"

class RuleLevel(str, Enum):
    ERROR = "CRITICA"
    WARNING = "ALTA"
    INFO = "MEDIA"
    SUGGESTION = "BASSA"

class TaskProfile(BaseModel):
    # Parametri Descrittivi
    type: str = "Execution"
    actor: str = "System"
    beneficiary: List[str] = []
    
    # Governance e Etica
    is_automated: bool = False
    acc_owner: Optional[str] = None
    critical_task: bool = False
    
    # Dati ed Equità
    sensitive_data: bool = False
    equity_action: EquityAction = EquityAction.NONE
    equity_note: Optional[str] = None
    criteria_defined: bool = False
    
    # Benessere ed Ergonomia
    impacts_wellbeing: bool = False
    outside_working_hours: bool = False
    default_action: bool = False

class BpmnNode(BaseModel):
    id: str
    name: str
    type_node: str # es. 'bpmn:serviceTask', 'bpmn:userTask', 'bpmn:exclusiveGateway'
    profile: Optional[TaskProfile] = None
    outgoing_flows: List[str] = [] # ID dei nodi successivi

class Violation(BaseModel):
    rule_number: int
    rule_name: str
    level: RuleLevel
    target_node: str
    message: str