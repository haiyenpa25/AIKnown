import time
import os
import typer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.last_run = 0

    def rebuild_graph(self):
        now = time.time()
        # Debounce 2 seconds
        if now - self.last_run < 2:
            return
        self.last_run = now
        
        typer.echo("\n[Watcher] Phát hiện thay đổi mã nguồn! Đang quét lại hệ thống...")
        start = time.time()
        
        # Gọi lại flow quét cơ bản từ cli.py (Bypass Typer CLI)
        from .scanner import Scanner
        from .parser import CodeParser
        from .store import ContextStore
        from .linker import GraphLinker
        from .ui_builder import UIBuilder
        
        scanner = Scanner(self.root_dir)
        store = ContextStore()
        parser = CodeParser()
        
        files = scanner.scan_files()
        if not files:
            return
            
        store.clear_database()
        temp_deps = []
        for rel_path, mtime in files:
            full_path = os.path.join(self.root_dir, rel_path)
            lang, symbols = parser.parse_file(full_path)
            file_node_id = f"file::{rel_path}"
            store.add_node(file_node_id, 'FILE', rel_path, rel_path, lang)
            for sym in symbols:
                node_id = f"{rel_path}::{sym['name']}"
                store.add_node(node_id, sym['type'], sym['name'], rel_path, lang, sym.get('docstring', ''))
                store.add_edge(file_node_id, node_id, 'CONTAINS')
                for dep in sym.get('dependencies', []):
                    temp_deps.append((node_id, dep))
                    
        linker = GraphLinker(store)
        linker.link_calls(temp_deps)
        
        builder = UIBuilder(store)
        builder.generate_html(open_browser=False)
        
        store.close()
        typer.echo(f"[Watcher] Cập nhật thành công trong {time.time() - start:.2f}s!")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.py', '.php', '.js', '.ts')):
            self.rebuild_graph()

def start_watcher(root_dir: str):
    typer.echo(f"Bắt đầu chế độ Live Sync Watchdog tại: {root_dir}")
    typer.echo("Nhấn Ctrl+C để thoát. Hãy mở Dashboard UI trên màn hình bên cạnh!")
    
    # Run first time completely
    handler = CodeChangeHandler(root_dir)
    handler.rebuild_graph()
    
    observer = Observer()
    observer.schedule(handler, path=root_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
