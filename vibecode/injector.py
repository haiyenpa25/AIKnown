import os
from .store import ContextStore

class Injector:
    def __init__(self, store: ContextStore):
        self.store = store

    def generate_context_for_file(self, target_filepath):
        lines = []
        lines.append(f"### ACTIVE FILE: {target_filepath}")
        
        cursor = self.store.conn.cursor()
        cursor.execute("SELECT id, content FROM nodes WHERE file_path=? AND type='FILE'", (target_filepath,))
        row = cursor.fetchone()
        if not row:
            return f"Không tìm thấy file {target_filepath} trong CSDL. Hãy chạy `vibecode scan`."
        
        file_id, summary = row
        lines.append(f"SUMMARY: {summary if summary else 'N/A'}")
        
        symbols = self.store.get_node_context(target_filepath) # returns id, name, type
        if symbols:
            lines.append("\n### SYMBOLS IN FILE:")
            for sym in symbols:
                node_id, symbol_name, symbol_type = sym
                lines.append(f"- [{symbol_type}] {symbol_name}")
                outbound = self.store.get_outbound(node_id)
                if outbound:
                    lines.append(f"  -> Calls: {', '.join(outbound[:10])}" + ("..." if len(outbound) > 10 else ""))
                    
        # Inject protocol token
        token = self.generate_handover_token(target_filepath)
        lines.insert(0, token)
        lines.insert(1, "\n---")
        
        return "\n".join(lines)
        
    def generate_handover_token(self, active_file):
        context_id = "sess_current"
        db_path = self.store.db_path
        task = self.store.get_state('CURRENT_TASK') or 'None'
        
        token = f"""
[VIBECODE_HANDOVER_TOKEN]
CONTEXT_ID: "{context_id}"
ACTIVE_FOCUS: ["{active_file}"]
CURRENT_TASK: "{task}"
DB_PATH: "{db_path}"
[/VIBECODE_HANDOVER_TOKEN]
"""
        return token.strip()
