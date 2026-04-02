import typer
import os
import time
from .scanner import Scanner
from .parser import CodeParser
from .store import ContextStore
from .injector import Injector

app = typer.Typer(help="VibeCode: AI Context Injector & Code Knowledge Store")

@app.command()
def init():
    """Khởi tạo CSDL VibeCode tại thư mục hiện tại."""
    store = ContextStore()
    typer.echo(f"Đã khởi tạo VibeCode DB tại {store.db_path}")
    store.close()

@app.command()
def scan(root_dir: str = "."):
    """Quét và phân tích toàn bộ thư mục."""
    typer.echo("Đang quét thư mục...")
    start_time = time.time()
    
    scanner = Scanner(root_dir)
    store = ContextStore()
    parser = CodeParser()
    
    files = scanner.scan_files()
    if not files:
        typer.echo("Không tìm thấy file phù hợp (py, php, js, ts).")
        return
        
    typer.echo(f"Đã quét xong. Tìm thấy {len(files)} files cần phân tích.")
    
    for rel_path, mtime in files:
        full_path = os.path.join(root_dir, rel_path)
        lang, symbols = parser.parse_file(full_path)
        
        # SQLite Upsert
        file_id = store.upsert_file(rel_path, lang, 'Source', mtime)
        store.clear_file_symbols(file_id)
        
        for sym in symbols:
            sid = store.add_symbol(file_id, sym['name'], sym['type'], sym['signature'], sym['docstring'])
            for dep in sym.get('dependencies', []):
                store.add_dependency(sid, dep)
    
    store.close()
    typer.echo(f"Hoàn tất lập chỉ mục trong {time.time() - start_time:.2f}s!")

@app.command()
def context(filepath: str):
    """Lấy VibeCode context dựa trên một file đang làm việc."""
    store = ContextStore()
    injector = Injector(store)
    
    output = injector.generate_context_for_file(filepath)
    store.close()
    
    typer.echo(output)

@app.command()
def graph(symbol: str):
    """Vẽ Call Graph (Sự phụ thuộc) của một hàm."""
    store = ContextStore()
    
    outbound = store.get_outbound_dependencies(symbol)
    inbound = store.get_inbound_dependencies(symbol)
    
    typer.echo(f"=== Sơ đồ gọi hàm (Call Graph) cho: {symbol} ===")
    
    typer.echo("\n[->] GỌI RA (Outbound Dependencies):")
    if not outbound:
        typer.echo("  (Không gọi hàm nào khác)")
    else:
        for out in outbound:
            typer.echo(f"  -> {out}")
            
    typer.echo("\n[<-] ĐƯỢC GỌI BỞI (Inbound Dependencies):")
    if not inbound:
        typer.echo("  (Không có hàm nào gọi tới)")
    else:
        for inb in inbound:
            typer.echo(f"  <- [{inb['type']}] {inb['name']} (tại {inb['file']})")
            
    store.close()

@app.command()
def state(key: str, value: str):
    """Cập nhật trạng thái project để AI nắm context."""
    store = ContextStore()
    store.upsert_state(key, value)
    store.close()
    typer.echo(f"Đã cập nhật state: {key} = {value}")

if __name__ == "__main__":
    app()
