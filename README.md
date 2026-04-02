# VibeCode Pipeline 🚀

VibeCode là hệ thống **Số hóa tri thức Code (Digitalizing Code Knowledge)**. Công cụ này xử lý vấn đề Context Window (giới hạn bộ nhớ) hoặc mất ngữ cảnh khi chuyển đổi giữa các mô hình AI (như Claude sang Gemini) bằng cách tạo ra một CSDL Local SQLite để lập bản đồ cấu trúc hàm, biến, class và quan hệ phụ thuộc lẫn nhau.

---

## Tính Năng Cốt Lõi

1. **Scanner Thông minh:** Quét siêu tốc và tự động bỏ qua các thư mục như `node_modules`, `vendor` hoặc bất kỳ file nào có trong `.gitignore`.
2. **AST Parser với Tree-sitter:** Đi sâu vào cây cú pháp (AST) của Python, PHP, Javascript/Typescript để bóc tách Function, Class, docstrings mà không làm chạy mã nguồn.
3. **Call Graph (Dependency Graph):** Vẽ bản đồ quan hệ: Hàm A đang gọi các hàm nào, và Hàm B đang bị những hàm nào gọi.
4. **Context Injector (Giao thức Handover):** Bơm một thẻ `[VIBECODE_HANDOVER_TOKEN]` kèm mã ID trạng thái, giúp các LLM liền mạch xử lý nhiệm vụ.

---

## Hướng Dẫn Cài Đặt 🛠️

Bạn có 2 cách để triển khai VibeCode tùy theo nhu cầu:

### Cách 1: Dùng Môi Trường Code Trực Tiếp (Dành cho Developer / User thông thường)
Chạy kịch bản tự động tải & cấu hình:
1. Mở thư mục dự án và click đúp vào file `install.bat`.
2. Đợi máy tải và cài đặt Python (nếu chưa có), sau đó thiết lập môi trường `.venv` với `requirements.txt`.
3. Trong Terminal/PowerShell, bắt đầu dùng lệnh: 
```bash
.\.venv\Scripts\python -m vibecode [lệnh]
```

### Cách 2: Đóng Gói Thành File Độc Lập `.exe` (Dành cho Phân phối)
Không cần cài đặt rườm rà. Phù hợp để gửi cho người khác dùng trực tiếp trên Windows.
1. Chạy file `build.bat`.
2. PyInstaller sẽ đóng gói bộ mã nguồn vào một file duy nhất tại thư mục `dist/vibecode.exe`.
3. Giờ đây bạn có thể ném `vibecode.exe` vào bất kỳ dự án nào hoặc ném vào ổ C, thiết lập PATH Variable để gọi `vibecode [lệnh]` mọi ngóc ngách hệ thống!

*(Dưới đây, tài liệu giả sử bạn đang dùng bản `.exe`. Nếu bạn dùng cách 1, thay `vibecode` bằng `.\.venv\Scripts\python -m vibecode`)*

---

## Hướng Dẫn Các Câu Lệnh (CLI) 💻

### 1. Quét Toàn Bộ Dự Án (Scan & Index)
Hãy đặt CLI tại thư mục gốc của dự án bạn đang làm, sau đó gõ:
```bash
vibecode scan
```
- **Tác dụng:** Nó tìm tất cả mã nguồn (Python, PHP, JS, TS) và cập nhật sơ đồ cây vào Database SQLite ẩn (`.vibecode/store.db`).
- **Thời điểm dùng:** Bất kỳ khi nào bạn tải code mới về, hoặc viết xong vài module mới.

### 2. Trích Xuất Ngữ Cảnh Cho AI (Context)
Bạn đang làm việc ở file `src/auth.js` và muốn hỏi AI về một lỗi trong đó? Đừng gửi cả file cho AI, hãy gửi ngữ cảnh VibeCode:
```bash
vibecode context src/auth.js
```
- **Kết quả trả về:** Giao thức kết hợp với danh sách Hàm / Call Graph liên quan. Bạn chỉ cần copy/paste kết quả này cho AI, AI sẽ tự hiểu được xung quanh hàm này liên kết với logic nào.

### 3. Vẽ Sơ Đồ Phụ Thuộc Của Hàm (Graph)
Bạn muốn biết trước khi sửa hàm `process_data`, nó sẽ ảnh hưởng ai?
```bash
vibecode graph process_data
```
- **Kết quả trả về:**
  - `Outbound`: Các hàm mà `process_data` phát ra (VD: nó lưu DB, hay gửi mail).
  - `Inbound`: Danh sách các Class / Controller đang gọi đến `process_data`. (Sửa hàm này thì các Class Inbound sẽ dính lỗi!).

### 4. Thiết Lập Điểm Nhớ / Session (State)
```bash
vibecode state CURRENT_TASK "Fixing login API bug caused by JWT expired"
```
- **Tác dụng:** Cập nhật nhiệm vụ bạn đang làm. Khi đổi từ ChatGPT sang Claude, Claude sẽ bắt được trạng thái này thông qua Handover Token và tự bắt tay làm tiếp!

---

## Cách Tương Tác Cùng LLM (Gemini / Claude / ChatGPT) 🤖

Khi bắt đầu một khung chat mới với AI:
1. Gõ `vibecode scan` ở máy tính của bạn.
2. Gõ `vibecode context <file_đang_sửa>`. Copy đầu ra.
3. Paste cho Model và dặn AI đọc, ví dụ: 
> "Đây là context của file tao đang làm. Bug đang ở hàm `login()`. Mày hãy phân tích các hàm được liệt kê trong Dependency Graph xem lỗi đến từ đâu."
4. Nếu AI yêu cầu đọc mã nguồn của hàm vệ tinh, bạn có thể tự mở hàm đó ra dán vào. Mọi thứ được kiểm soát chặt chẽ và không "ảo giác" (hallucination)!
