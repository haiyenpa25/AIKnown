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
        
        # Bảng Files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                language TEXT,
                type TEXT,
                last_modified REAL,
                summary TEXT
            )
        ''')
        
        # Bảng Symbols (Function, Class, Variables)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                name TEXT,
                type TEXT,
                signature TEXT,
                docstring TEXT,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Bảng Dependency
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                source_symbol_id INTEGER,
                target_symbol_name TEXT,
                FOREIGN KEY (source_symbol_id) REFERENCES symbols (id)
            )
        ''')

        # Bảng Trạng thái Handover
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def upsert_file(self, path, language, type_, last_modified):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO files (path, language, type, last_modified) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET 
                last_modified=excluded.last_modified
        ''', (path, language, type_, last_modified))
        self.conn.commit()
        
        cursor.execute("SELECT id FROM files WHERE path=?", (path,))
        return cursor.fetchone()[0]
        
    def clear_file_symbols(self, file_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM dependencies WHERE source_symbol_id IN (SELECT id FROM symbols WHERE file_id=?)", (file_id,))
        cursor.execute("DELETE FROM symbols WHERE file_id=?", (file_id,))
        self.conn.commit()

    def add_symbol(self, file_id, name, type_, signature, docstring):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO symbols (file_id, name, type, signature, docstring)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_id, name, type_, signature, docstring))
        self.conn.commit()
        return cursor.lastrowid
    
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
