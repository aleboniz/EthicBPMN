import streamlit as st
import streamlit.components.v1 as components
import json

def visualizza_bpmn_interattivo(xml_content, violations):
    xml_safe = json.dumps(xml_content)
    
    # Gerarchia pesi per il colore dominante
    weights = {"ERROR": 4, "WARNING": 3, "INFO": 2, "SUGGESTION": 1, "NONE": 0}
    
    audit_data = {}
    for v in violations:
        node_id = v.target_node
        level = v.level.name 
        if node_id not in audit_data:
            audit_data[node_id] = {"level": level, "messages": []}
        else:
            if weights.get(level, 0) > weights.get(audit_data[node_id]["level"], 0):
                audit_data[node_id]["level"] = level
        audit_data[node_id]["messages"].append(v.message)
    
    audit_json = json.dumps(audit_data)

    html_code = f"""
    <div id="canvas" style="height: 600px; width: 100%; border: 1px solid #e6e9ef; border-radius: 12px; background-color: #f8f9fa;"></div>
    
    <style>
        /* RESET BASE: Grigio neutro per Task e Gateway (rombi) */
        .djs-container .djs-visual rect, 
        .djs-container .djs-visual polygon {{
            fill: #fdfdfd !important;
            stroke: #999999 !important;
            stroke-width: 1px !important;
            transition: fill 0.2s, stroke 0.2s !important;
        }}

        /* HOVER: Colori per rettangoli (Task) e poligoni (Gateway) */
        .hover-error.djs-shape .djs-visual rect, .hover-error.djs-shape .djs-visual polygon {{ fill: #ffdbdb !important; stroke: #ff0000 !important; stroke-width: 3px !important; }}
        .hover-warning.djs-shape .djs-visual rect, .hover-warning.djs-shape .djs-visual polygon {{ fill: #ffeacc !important; stroke: #ff8000 !important; stroke-width: 3px !important; }}
        .hover-info.djs-shape .djs-visual rect, .hover-info.djs-shape .djs-visual polygon {{ fill: #fff9db !important; stroke: #fab005 !important; stroke-width: 2px !important; }}
        .hover-suggestion.djs-shape .djs-visual rect, .hover-suggestion.djs-shape .djs-visual polygon {{ fill: #fdffdb !important; stroke: #d4d400 !important; stroke-width: 2px !important; }}
        .hover-none.djs-shape .djs-visual rect, .hover-none.djs-shape .djs-visual polygon {{ fill: #e6ffed !important; stroke: #28a745 !important; stroke-width: 2px !important; }}

        .bpmn-tooltip {{
            position: fixed; background: white; border-radius: 8px; padding: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2); z-index: 9999; pointer-events: none;
            max-width: 280px; font-family: sans-serif; font-size: 13px; display: none;
            border-left: 6px solid #ccc; line-height: 1.4;
        }}
        .level-ERROR {{ border-left-color: #ff0000; }}
        .level-WARNING {{ border-left-color: #ff8000; }}
        .level-INFO {{ border-left-color: #fab005; }}
        .level-SUGGESTION {{ border-left-color: #d4d400; }}
        .level-NONE {{ border-left-color: #28a745; }}
    </style>

    <div id="tooltip" class="bpmn-tooltip"></div>
    <script src="https://unpkg.com/bpmn-js@16.4.0/dist/bpmn-viewer.production.min.js"></script>
    
    <script>
      (async function() {{
        const bpmnXML = {xml_safe};
        const auditData = {audit_json};
        const bpmnViewer = new BpmnJS({{ container: '#canvas' }});
        const tooltip = document.getElementById('tooltip');

        try {{
          await bpmnViewer.importXML(bpmnXML);
          const canvas = bpmnViewer.get('canvas');
          const eventBus = bpmnViewer.get('eventBus');
          
          canvas.zoom('fit-viewport', 'center');

          // Funzione per capire se l'elemento è un Task o un Gateway
          function isAuditable(element) {{
            return element.type.includes('Task') || element.type.includes('Gateway');
          }}

          eventBus.on('element.hover', function(e) {{
            const element = e.element;
            if (isAuditable(element)) {{
                const data = auditData[element.id];
                const level = data ? data.level : 'NONE';
                
                canvas.addMarker(element.id, 'hover-' + level.toLowerCase());

                tooltip.className = 'bpmn-tooltip level-' + level;
                tooltip.style.display = 'block';
                
                let header = element.type.includes('Gateway') ? 'Audit Gateway: ' : 'Audit Task: ';
                tooltip.innerHTML = '<b>' + header + level + '</b><br>' + 
                                   (data ? data.messages : ['Nessuna criticità rilevata.']).map(m => '• ' + m).join('<br>');
            }}
          }});

          eventBus.on('element.out', function(e) {{
            if (isAuditable(e.element)) {{
                const data = auditData[e.element.id];
                const level = data ? data.level : 'NONE';
                canvas.removeMarker(e.element.id, 'hover-' + level.toLowerCase());
                tooltip.style.display = 'none';
            }}
          }});

          document.addEventListener('mousemove', e => {{
            let windowHeight = window.innerHeight;
            let windowWidth = window.innerWidth;
            let tooltipHeight = tooltip.offsetHeight || 150;
            let tooltipWidth = tooltip.offsetWidth || 250;

            if (e.clientY + tooltipHeight + 20 > windowHeight) {{
                tooltip.style.top = (e.clientY - tooltipHeight - 15) + 'px';
            }} else {{
                tooltip.style.top = (e.clientY + 15) + 'px';
            }}

            if (e.clientX + tooltipWidth + 20 > windowWidth) {{
                tooltip.style.left = (e.clientX - tooltipWidth - 15) + 'px';
            }} else {{
                tooltip.style.left = (e.clientX + 15) + 'px';
            }}
          }});

        }} catch (err) {{ console.error(err); }}
      }})();
    </script>
    """
    components.html(html_code, height=650)