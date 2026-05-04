# src/ai_complete.py
import re
from src.models import TaskProfile

class AICompleter:
    def __init__(self, ai_assistant):
        self.client = ai_assistant.client

    def complete_missing_profiles(self, nodes: list):
        for node in nodes:
            if node.profile is not None:
                print(f"Skipping '{node.name}': Profilo già presente nell'XML (validazione manuale).")
                continue

            node_type_lower = node.type_node.lower()
            is_auto_bpmn = any(x in node_type_lower for x in ["servicetask", "businessruletask", "scripttask"])
            
            name_lower = node.name.lower()

            suggested_actor = node.lane if node.lane else "System" if is_auto_bpmn else "User"
        
            suggested_beneficiary = []
            if node.pool and any(x in node.pool.lower() for x in ["client", "candidat", "customer", "patient", "user"]):
                suggested_beneficiary = [node.pool]

            sensitive_keywords = [
                "cv", "curriculum", "identit", "passport", "document", "id_check", "birth", "anagraf",
                "salary", "stipendio", "ral", "busta_paga", "finanz", "bank", "iban", "contract",
                "softskill", "assessment", "psyc", "personality", "attitudinal", "comportament", "tratti",
                "health", "sanitari", "biometric", "facial", "voice", "audio_analysis", "medical", 
                "religion", "political", "union", "disability", "categoria_protetta",
                "background_check", "criminal", "penale", "social_media", "reference", "voto", "laurea"
            ]
            is_sensitive_val = any(w in name_lower for w in sensitive_keywords)

            critical_keywords = [
                "screen", "filter", "select", "scelta", "cernita", "shortlist", "eligible",
                "assess", "evaluat", "valutazione", "test", "exam", "ranking", "rank", "punteggio", "score",
                "hire", "assunzion", "reject", "scarto", "final_decision", "offert", "approv",
                "monitor", "tracking", "performance", "produttivit", "efficiency"
            ]
            is_critical_val = any(w in name_lower for w in critical_keywords)

            prompt = f"""
            Analizza questo task BPMN nel suo contesto organizzativo:
            - Task Name: '{node.name}'
            - BPMN Type: {node.type_node}
            - Pool (Organization): {node.pool if node.pool else 'N/A'}
            - Lane (Role/Unit): {node.lane if node.lane else 'N/A'}

            Valori determinati: Automated={is_auto_bpmn}, Sensitive={is_sensitive_val}, Critical={is_critical_val}

            Genera i 6 parametri etici separati da virgola:
            1. SENSITIVE: {is_sensitive_val}
            2. AUTOMATED: {is_auto_bpmn}
            3. CRITICAL: {is_critical_val}
            4. WELLBEING: True se implica stress da monitoraggio, analisi psicologica o valutazione invasiva.
            5. CRITERIA: True se il task richiede regole oggettive documentate.
            6. OFF-HOURS: True se invia notifiche/email automatiche fuori orario.

            Rispondi solo con i 6 valori booleani separati da virgola (es: True, True, True, False, True, False).
            """

            try:
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                
                res_raw = response.choices[0].message.content.strip()
                booleans = re.findall(r'\b(TRUE|FALSE)\b', res_raw, re.IGNORECASE)
                
                if len(booleans) >= 6:
                    node.profile = TaskProfile(
                        actor=suggested_actor,
                        beneficiary=suggested_beneficiary,
                        sensitive_data=is_sensitive_val,
                        is_automated=is_auto_bpmn,
                        critical_task=is_critical_val,
                        impacts_wellbeing=(booleans[3].upper() == "TRUE"),
                        criteria_defined=(booleans[4].upper() == "TRUE"),
                        outside_working_hours=(booleans[5].upper() == "TRUE")
                    )
                else:
                    print(f"   [!] Errore: L'AI ha risposto con pochi valori ({len(booleans)})")
                
            except Exception as e:
                print(f"Errore analisi '{node.name}': {e}")