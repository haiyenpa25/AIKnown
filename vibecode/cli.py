import typer
import os
import time
import json
from .scanner import Scanner
from .parser import CodeParser
from .store import ContextStore
from .injector import Injector
from .linker import GraphLinker
from .ui_builder import UIBuilder

app = typer.Typer(help="VibeCode: AI Context Injector & Code Knowledge Store")

@app.command()
def init():
    """Khởi tạo CSDL VibeCode."""
    store = ContextStore()
    typer.echo(f"Đã khởi tạo VibeCode DB tại {store.db_path}")
    store.close()

@app.command()
def scan(root_dir: str = "."):
    """Quét và phân tích toàn bộ thư mục (Pha 1: Nodes, Pha 2: Edges)."""
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
    store.clear_database()
    
    temp_deps = []
    
    # PASS 1: Đẩy tất cả Nodes
    for rel_path, mtime in files:
        full_path = os.path.join(root_dir, rel_path)
        lang, symbols = parser.parse_file(full_path)
        
        file_node_id = f"file::{rel_path}"
        store.add_node(file_node_id, 'FILE', rel_path, rel_path, lang)
        
        for sym in symbols:
            node_id = f"{rel_path}::{sym['name']}"
            store.add_node(node_id, sym['type'], sym['name'], rel_path, lang, sym['docstring'])
            store.add_edge(file_node_id, node_id, 'CONTAINS')
            
            for dep in sym.get('dependencies', []):
                temp_deps.append((node_id, dep))
                
    # PASS 2: Nối Edges
    linker = GraphLinker(store)
    linker.link_calls(temp_deps)
    
    store.close()
    typer.echo(f"Hoàn tất lập chỉ mục Graph trong {time.time() - start_time:.2f}s!")

@app.command()
def context(filepath: str):
    """Lấy VibeCode context dựa trên một file."""
    store = ContextStore()
    injector = Injector(store)
    output = injector.generate_context_for_file(filepath)
    store.close()
    typer.echo(output)

@app.command()
def graph(symbol: str):
    """Vẽ Call Graph (Sự phụ thuộc) của một hàm."""
    store = ContextStore()
    node = store.get_node_by_name(symbol)
    if not node:
        typer.echo(f"Không tìm thấy Node nào mang tên: {symbol}")
        return
    
    node_id, node_type, file_path = node
    outbound = store.get_outbound(node_id)
    inbound = store.get_inbound(node_id)
    
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
            typer.echo(f"  <- [{inb[1]}] {inb[0]} (tại {inb[2]})")
            
    store.close()

@app.command()
def ui():
    """Sinh file HTML và mở Sơ đồ mạng nhện (Visual Graph) trên Browser."""
    store = ContextStore()
    from .ui_builder import UIBuilder
    builder = UIBuilder(store)
    output_file = builder.generate_html()
    store.close()
    typer.echo(f"Đã xuất sơ đồ ra file {output_file} và mở trên trình duyệt!")

@app.command()
def prompt(task: str, filepath: str):
    """Lấy Ngữ cảnh File và nấu thành Prompt chuẩn gửi đi cho AI (như Antigravity/Gemini)"""
    store = ContextStore()
    from .injector import Injector
    injector = Injector(store)
    context_str = injector.generate_context_for_file(filepath)
    store.close()
    
    prompt_template = f"""[THÔNG ĐIỆP GỬI MÔ HÌNH AI]
Chào AI, tôi đang thực hiện nhiệm vụ: "{task}".
Dưới đây là Ngữ cảnh VibeCode (Graph Context) hiện tại của file `{filepath}`:

```markdown
{context_str}
```

MỆNH LỆNH THỰC THI (CHỐNG ẢO GIÁC LỖI):
1. Dựa vào các Hàm được liệt kê trong File này (và các hàm Outbound mà chúng gọi đi), hãy phân tích sơ đồ logic và tư vấn xem việc làm "{task}" nên can thiệp vào Hàm nào là hợp lý và an toàn nhất?
2. Có hàm Inbound nào bị ảnh hưởng (Break) nếu tôi sửa logic ở File này không?
3. Tuyệt đối KHÔNG TỰ ĐOÁN MÓ Kịch Bản/Code của các hàm Outbound. Nếu bạn cho rằng mình cần đọc nội dung gốc của một hàm Outbound, hãy yêu cầu tôi dùng VibeCode mở ra cho bạn xem.
========================="""
    
    out_file = "AI_PROMPT_TO_COPY.txt"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(prompt_template)
        
    typer.echo(f"Đã tạo file {out_file} chứa khuôn mẫu Prompt siêu cấp chống Lỗi. Bạn chỉ cần Copy và paste gửi ngay cho AI.")

@app.command()
def state(key: str, value: str):
    store = ContextStore()
    store.upsert_state(key, value)
    store.close()
    typer.echo(f"Đã cập nhật state: {key} = {value}")

@app.command()
def watch(root_dir: str = "."):
    """Bật chế độ Giám sát (Watchdog) - Tự động cập nhật Graph khi lưu file."""
    from .watcher import start_watcher
    start_watcher(root_dir)

if __name__ == "__main__":
    app()
