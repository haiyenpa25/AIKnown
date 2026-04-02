import json
import os
import webbrowser

class UIBuilder:
    def __init__(self, store):
        self.store = store

    def generate_html(self, output_file='vibecode_graph.html', open_browser=True):
        nodes_db = self.store.get_nodes()
        edges_db = self.store.get_edges()
        
        elements = []
        
        # Thêm Nodes
        for n_id, name, type_, file_path in nodes_db:
            if type_ == 'FILE':
                # File node là một Parent Node (Hộp chứa)
                elements.append({
                    "data": {
                        "id": n_id,
                        "label": name,
                        "type": type_
                    }
                })
            else:
                color = "#ccc"
                if type_ == 'Class':
                    color = "#f54254" # Đỏ rực rỡ
                elif type_ == 'Function':
                    color = "#E1B000" # Vàng sang trọng
                elif type_ == 'External':
                    color = "#64748b" # Xám tro
                
                # Logic bao bọc (Compound Node): Node này nằm TRONG file
                elements.append({
                    "data": {
                        "id": n_id,
                        "label": name,
                        "type": type_,
                        "color": color,
                        "parent": f"file::{file_path}"
                    }
                })
            
        # Thêm Edges
        for source, target, relation in edges_db:
            if relation == 'CONTAINS':
                continue
                
            elements.append({
                "data": {
                    "source": source,
                    "target": target,
                    "label": relation
                }
            })
            
        # Export JS Data File cho Live Sync Polling
        data_script = f"window.VIBECODE_ELEMENTS = {json.dumps(elements)};"
        with open('vibecode_graph_data.js', 'w', encoding='utf-8') as f:
            f.write(data_script)
            
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VibeCode Enhanced Visuals</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #0f172a; color: #f8fafc; overflow: hidden; }}
    #cy {{ width: 100vw; height: 100vh; display: block; }}
    #info {{ position: absolute; top: 15px; left: 15px; background: rgba(30, 41, 59, 0.9); padding: 15px; border-radius: 8px; z-index: 10; max-height: 90vh; overflow-y: auto; width: 320px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); border: 1px solid #334155; backdrop-filter: blur(4px); }}
    h2 {{ margin-top: 0; border-bottom: 1px solid #334155; padding-bottom: 10px; font-size: 1.2rem; color: #38bdf8; display:flex; justify-content:space-between; align-items:center; }}
    #sync-status {{ width: 10px; height: 10px; border-radius: 50%; background: #22c55e; display: inline-block; box-shadow: 0 0 8px #22c55e; }}
    p.subtitle {{ font-size: 12px; color: #94a3b8; line-height: 1.4; }}
    .badge {{ background: #1e293b; padding: 3px 6px; border-radius: 4px; font-size: 11px; color: #cbd5e1; border: 1px solid #475569; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: #475569; border-radius: 4px; }}
</style>
</head>
<body>
<div id="info">
    <h2>VibeCode System <span id="sync-status" title="Live Sync Active"></span></h2>
    <p class="subtitle">Dùng cuộn chuột để <b>Zoom</b>, Kéo thả vùng trống để <b>Di chuyển</b>.</p>
    <div id="selected-info" style="font-size: 13px; margin-top: 15px; background: #0f172a; padding: 10px; border-radius: 6px; border: 1px dashed #334155;">
        <i style="color: #64748b;">Khởi tạo... Hãy bấm vào một Hình Chữ Nhật (File) nhỏ hoặc một Hình Tròn (Hàm/Class) trên đồ thị.</i>
    </div>
</div>
<div id="cy"></div>

<script>
    var cy = cytoscape({{
        container: document.getElementById('cy'),
        style: [
            {{
                selector: ':parent',
                style: {{
                    'background-opacity': 0.05,
                    'background-color': '#38bdf8',
                    'border-width': 2,
                    'border-style': 'dashed',
                    'border-color': '#38bdf8',
                    'border-opacity': 0.6,
                    'label': 'data(label)',
                    'color': '#7dd3fc',
                    'text-valign': 'top',
                    'text-halign': 'center',
                    'font-size': '16px',
                    'font-weight': 'bold',
                    'text-margin-y': -8,
                    'padding': 15
                }}
            }},
            {{
                selector: 'node:child',
                style: {{
                    'background-color': 'data(color)',
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-outline-color': '#0f172a',
                    'text-outline-width': 2,
                    'font-size': '11px',
                    'width': 25,
                    'height': 25,
                }}
            }},
            {{
                selector: 'edge',
                style: {{
                    'width': 1.5,
                    'line-color': '#475569',
                    'target-arrow-color': '#475569',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'font-size': '10px',
                    'color': '#94a3b8',
                    'arrow-scale': 1.2
                }}
            }},
            {{ selector: '.dimmed', style: {{ 'opacity': 0.15 }} }},
            {{ selector: 'node.highlighted', style: {{ 'border-width': 4, 'border-color': '#fff', 'z-index': 999 }} }},
            {{ selector: 'edge.highlighted', style: {{ 'width': 3, 'line-color': '#38bdf8', 'target-arrow-color': '#38bdf8', 'z-index': 999 }} }}
        ],
        layout: {{
            name: 'cose',
            idealEdgeLength: 60,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 30,
            randomize: false,
            componentSpacing: 100,
            nodeRepulsion: 400000,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        }}
    }});
    
    // Core tính năng tương tác
    cy.on('tap', function(evt){{
        cy.elements().removeClass('highlighted dimmed');
        document.getElementById('selected-info').innerHTML = '<i style="color: #64748b;">Mạng nhện đã reset. Bấm lại vào các đối tượng để hiển thị liên kết...</i>';

        var target = evt.target;
        if (target !== cy) {{
            if (target.isNode() && target.isParent()) {{
               var childrenCount = target.children().length;
               document.getElementById('selected-info').innerHTML = 
                '<div style="margin-bottom: 8px;"><strong>File Mở Rộng:</strong> <span style="color:#38bdf8">' + target.data('label') + '</span></div>' +
                '<div style="margin-bottom: 8px;"><span class="badge">Đang chứa ' + childrenCount + ' phần tử con</span></div>';
            }} 
            else if (target.isNode() && target.isChild()) {{
                var neighborhood = target.closedNeighborhood();
                cy.elements().difference(neighborhood).addClass('dimmed');
                
                var p = target.parent();
                if(p.length) p.removeClass('dimmed');
                
                neighborhood.addClass('highlighted');
                
                var inDegrees = target.incomers('edge').length;
                var outDegrees = target.outgoers('edge').length;
                
                var parLabel = p.length ? p.data('label') : 'External/Global';
                
                document.getElementById('selected-info').innerHTML = 
                    '<div style="margin-bottom: 8px;"><strong>Định danh:</strong> <span style="color:#fde047">' + target.data('label') + '</span></div>' +
                    '<div style="margin-bottom: 8px;"><strong>Phân Loại:</strong> <span class="badge">' + target.data('type') + '</span></div>' +
                    '<div style="margin-bottom: 8px;"><strong>Nằm trong:</strong> <span style="color:#cbd5e1">' + parLabel + '</span></div>' +
                    '<hr style="border-color:#334155; margin: 10px 0;" />' +
                    '<div style="margin-bottom: 5px;"><strong>Nhận vào (Inbound):</strong> ' + inDegrees + ' mũi tên</div>' +
                    '<div style="margin-bottom: 5px;"><strong>Phát ra (Outbound):</strong> ' + outDegrees + ' mũi tên</div>';
            }}
        }}
    }});

    // === LIVE SYNC ENGINE ===
    window.currentDataStr = "";
    
    function loadData() {{
        var script = document.createElement('script');
        script.id = 'vibe-data';
        script.src = 'vibecode_graph_data.js?t=' + new Date().getTime(); // Anti-cache
        script.onload = function() {{
            if (window.VIBECODE_ELEMENTS) {{
                var newStr = JSON.stringify(window.VIBECODE_ELEMENTS);
                if (window.currentDataStr !== newStr) {{
                    window.currentDataStr = newStr;
                    cy.elements().remove();
                    cy.add(window.VIBECODE_ELEMENTS);
                    cy.layout({{
                        name: 'cose',
                        idealEdgeLength: 60, nodeOverlap: 20, fit: true,
                        padding: 30, componentSpacing: 100, nodeRepulsion: 400000
                    }}).run();
                    
                    var status = document.getElementById('sync-status');
                    status.style.background = '#fbbf24'; // Flash yellow
                    setTimeout(() => status.style.background = '#22c55e', 500);
                }}
            }}
        }};
        document.head.appendChild(script);
        setTimeout(() => {{ if(script.parentNode) script.remove(); }}, 500); // Cleanup DOM
    }}
    
    loadData(); // Load first time
    setInterval(loadData, 2000); // Poll every 2 seconds
</script>
</body>
</html>
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if open_browser:
            webbrowser.open('file://' + os.path.realpath(output_file))
        return output_file
