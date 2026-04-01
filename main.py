# main.py
import os
from src.parser import BpmnParser
from src.rule_engine import EthicRuleEngine
from src.ai_assistant import AIAssistant
from src.reporter import ReportGenerator

def main():
    print("Avvio del motore EthicBPMN...")
    
    # PER TEST: Crea un file XML finto se non esiste, in modo che il codice non vada in crash
    test_file = "data/test_process.bpmn"
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" id="Definitions_1">
              <bpmn:process id="Process_1" isExecutable="true">
                <bpmn:serviceTask id="Task_1" name="Scarto CV Automatico" />
                <bpmn:sendTask id="Task_2" name="Invio Email Notifica" />
                <bpmn:sequenceFlow id="Flow_1" sourceRef="Task_1" targetRef="Task_2" />
              </bpmn:process>
            </bpmn:definitions>""")

    # 1. Parsing
    print("Parsing del file BPMN...")
    parser = BpmnParser(test_file)
    nodes = parser.parse()
    
    # 2. Rule Engine (Analisi Strutturale)
    print("Esecuzione delle regole etiche...")
    engine = EthicRuleEngine(nodes)
    violations = engine.run_all_rules()
    metrics = engine.calculate_eps_metrics() # <-- NUOVA RIGA: Calcolo dei punteggi!
    
    # 3. AI Assistant (Analisi Semantica)
    print("Richiesta feedback a GroqCloud...")
    ai_assistant = AIAssistant()
    ai_feedback = ai_assistant.analyze_process_semantics(nodes)
    
    # 4. Generazione Output (Passiamo anche le metriche!)
    print("Generazione del report...")
    ReportGenerator.generate_markdown(violations, ai_feedback, metrics) # <-- MODIFICATA
    print("Analisi completata")

if __name__ == "__main__":
    main()