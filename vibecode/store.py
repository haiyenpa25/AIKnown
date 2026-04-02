import sqlite3
import os

class ContextStore:
    def __init__(self, db_path='.vibecode/store.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Bảng cấu hình/trạng thái chung
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Bảng Nodes (Đỉnh)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                file_path TEXT,
                language TEXT,
                content TEXT
            )
        ''')
        
        # Bảng Edges (Cạnh)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                source_id TEXT,
                target_id TEXT,
                relation_type TEXT,
                FOREIGN KEY (source_id) REFERENCES nodes (id),
                FOREIGN KEY (target_id) REFERENCES nodes (id),
                UNIQUE(source_id, target_id, relation_type)
            )
        ''')

        self.conn.commit()
    
    def clear_database(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM edges")
        cursor.execute("DELETE FROM nodes")
        self.conn.commit()

    def add_node(self, node_id, type_, name, file_path, language, content=""):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO nodes (id, type, name, file_path, language, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node_id, type_, name, file_path, language, content))
        self.conn.commit()
        
    def add_edge(self, source_id, target_id, relation_type="CALLS"):
        if not target_id: return
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO edges (source_id, target_id, relation_type)
            VALUES (?, ?, ?)
        ''', (source_id, target_id, relation_type))
        self.conn.commit()

    def get_nodes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, type, file_path FROM nodes")
        return cursor.fetchall()
        
    def get_edges(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT source_id, target_id, relation_type FROM edges")
        return cursor.fetchall()

    def find_node_by_name(self, name):
        cursor = self.conn.cursor()
        # 1. Tìm chính xác (Exact match FQDN hoặc tên toàn cục)
        cursor.execute("SELECT id FROM nodes WHERE name = ?", (name,))
        rows = cursor.fetchall()
        if len(rows) == 1:
            return rows[0][0]
        elif len(rows) > 1:
            return rows[0][0]
            
        # 2. Tìm Heuristic (VD: trong code gọi 'save', trong DB có 'User.save')
        cursor.execute("SELECT id FROM nodes WHERE name LIKE ?", (f'%.{name}',))
        rows = cursor.fetchall()
        if len(rows) == 1:
            # Phát hiện duy nhất 1 thằng khớp (VD: chỉ có 1 class có hàm save)
            return rows[0][0]
        elif len(rows) > 1:
            # Nếu có nhiều class cùng xài hàm save, heuristic tạm thời lấy thằng đầu tiên
            # TODO tương lai: Tính File Proximity
            return rows[0][0]
            
        # 3. Tìm theo PHP namespace (VD: gọi 'save', trong DB có 'User::save')
        cursor.execute("SELECT id FROM nodes WHERE name LIKE ?", (f'%::{name}',))
        rows = cursor.fetchall()
        if len(rows) >= 1:
            return rows[0][0]
            
        return None

    def get_node_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, type, file_path FROM nodes WHERE name = ?", (name,))
        return cursor.fetchone()

    # Lấy thông tin Context
    def get_node_context(self, file_path):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, type FROM nodes WHERE file_path = ? AND type != 'FILE'", (file_path,))
        return cursor.fetchall()
        
    def get_outbound(self, node_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT n.name FROM edges e JOIN nodes n ON e.target_id = n.id WHERE e.source_id = ? AND e.relation_type = 'CALLS'", (node_id,))
        return [r[0] for r in cursor.fetchall()]

    def get_inbound(self, node_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT n.name, n.type, n.file_path FROM edges e JOIN nodes n ON e.source_id = n.id WHERE e.target_id = ? AND e.relation_type = 'CALLS'", (node_id,))
        return cursor.fetchall()

    def upsert_state(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO state (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        ''', (key, value))
        self.conn.commit()
        
    def get_state(self, key):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM state WHERE key=?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def close(self):
        self.conn.close()
