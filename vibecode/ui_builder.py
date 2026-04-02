import json
import os
import webbrowser

class UIBuilder:
    def __init__(self, store):
        self.store = store

    def generate_html(self, output_file='vibecode_graph.html'):
        nodes_db = self.store.get_nodes()
        edges_db = self.store.get_edges()
        
        elements = []
        
        # Add Nodes
        for n_id, name, type_, file_path in nodes_db:
            color = "#ccc"
            if type_ == 'FILE':
                color = "#4287f5" # Blue
            elif type_ == 'Class':
                color = "#f54254" # Red
            elif type_ == 'Function':
                color = "#42f560" # Green
                
            elements.append({
                "data": {
                    "id": n_id,
                    "label": name,
                    "type": type_,
                    "color": color
                }
            })
            
        # Add Edges
        for source, target, relation in edges_db:
            elements.append({
                "data": {
                    "source": source,
                    "target": target,
                    "label": relation
                }
            })
            
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>VibeCode Call Graph</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
<style>
    body {{ font-family: sans-serif; margin: 0; padding: 0; background: #1e1e1e; color: white; }}
    #cy {{ width: 100vw; height: 100vh; display: block; }}
    #info {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 10px; border-radius: 5px; z-index: 10; max-height: 90vh; overflow-y: auto; width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    h2 {{ margin-top: 0; border-bottom: 1px solid #444; padding-bottom: 5px; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: #888; border-radius: 4px; }}
</style>
</head>
<body>
<div id="info">
    <h2>VibeCode Graph</h2>
    <p style="font-size: 13px; color: #aaa;">Zoom và kéo thả để điều hướng mạng lưới phụ thuộc.</p>
    <div id="selected-info" style="font-size: 14px; margin-top: 15px;">
        <i>Nhấn vào một Node để xem chi tiết...</i>
    </div>
</div>
<div id="cy"></div>
<script>
    var elements = {json.dumps(elements)};
    
    var cy = cytoscape({{
        container: document.getElementById('cy'),
        elements: elements,
        style: [
            {{
                selector: 'node',
                style: {{
                    'background-color': 'data(color)',
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-outline-color': '#000',
                    'text-outline-width': 2,
                    'font-size': '12px'
                }}
            }},
            {{
                selector: 'edge',
                style: {{
                    'width': 2,
                    'line-color': '#888',
                    'target-arrow-color': '#888',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'color': '#aaa',
                    'text-rotation': 'autorotate'
                }}
            }}
        ],
        layout: {{
            name: 'cose',
            idealEdgeLength: 100,
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
    
    cy.on('tap', 'node', function(evt){{
        var node = evt.target;
        var inDegrees = node.incomers('edge').length;
        var outDegrees = node.outgoers('edge').length;
        document.getElementById('selected-info').innerHTML = 
            '<div style="margin-bottom: 5px;"><strong>Tên:</strong> <span style="color:#42f560">' + node.data('label') + '</span></div>' +
            '<div style="margin-bottom: 5px;"><strong>Loại:</strong> ' + node.data('type') + '</div>' +
            '<div style="margin-bottom: 5px;"><strong>Bị gọi:</strong> ' + inDegrees + ' lần</div>' +
            '<div style="margin-bottom: 5px;"><strong>Gọi đi:</strong> ' + outDegrees + ' lần</div>';
    }});
</script>
</body>
</html>
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        webbrowser.open('file://' + os.path.realpath(output_file))
        return output_file
