# Đặc tả Kiến trúc Hệ thống VibeCode (VibeCode Specification)
Tài liệu này định nghĩa tầm nhìn và kiến trúc kỹ thuật của VibeCode - biến nó thành hệ thống sinh thái "Code Intelligence" phục vụ trực tiếp cho các Mô hình Ngôn ngữ Lớn (LLM).

---

## 1. Tuyên ngôn Giải pháp (The Problem to Solve)

Khi giao codebase cho AI để "đọc hiểu và code", lập trình viên gặp 3 chướng ngại lớn:
1. **Lãng phí Token:** Nhồi nguyên file lớn hoặc nhiều file gây tốn kém, dễ tràn giới hạn khung chứa (Context Window) và làm AI chậm đi, sinh ảo giác (Hallucination).
2. **Mất Dấu Kiến Trúc:** Khi sửa ở `A()`, AI không biết thằng `B()` đang gọi `A()` ở file khác, dẫn đến đập vỡ hệ thống (Breaking changes).
3. **Mù lòa trạng thái:** Chuyển từ AI này (Gemini) sang AI khác (Claude) khiến bối cảnh công việc bị đứt đoạn.

VibeCode giải quyết triệt để 3 điều này thông qua Kiến trúc Đồ thị (Graph Architecture).

---

## 2. Thiết kế Kiến trúc (Core Architecture)

### 2.1. Tầng Trích Xuất (Graph AST)
Hệ thống không ĐỌC CHỮ (RegEx) mà ĐỌC NGỮ NGHĨA bằng `Tree-sitter`.
- **Đỉnh (Nodes):** Mọi thành phần trong mã nguồn (File, Class, Function, Variable) đều bị bắt sống thành 1 Node. Lộ trình tiếp theo sẽ nạp luôn cả các thư viện ngoài (Numpy, React...) thành `External Nodes` dạng Xám để AI nhận biết Framework đang dùng.
- **Cạnh (Edges):** Không chỉ lưu liên kết "ai gọi ai", mà hệ thống Linker sẽ phân tích đường dẫn tuyệt đối (FQDN) để nối mũi tên chuẩn xác 100%, kể cả 2 file có 2 hàm trùng tên nhau (Tránh ảo giác Linker).

### 2.2. Chiến lược Tối ưu Token (Graph-Context Slicing)
VibeCode áp dụng phương pháp **Cắt lát Đồ thị (Slicing)** thay vì nộp (dump) toàn bộ Text:
- **Nguyên lý:** Nhận vào Tọa độ do Dev xác định (Ví dụ file `auth.js`), hệ thống chỉ rà hạt Node tỏa ra bán kính *Bậc 1* hoặc *Bậc 2*.
- **Kết quả:** Prompt vứt cho AI chỉ chứa *Mô tả Tóm lược* và *Danh sách liên kết* của đúng vùng đó.
- **Tiết kiệm Token (Thực Tế):** Tiết kiệm 80-90% token so với ném toàn bộ mã nguồn. Giảm từ 20,000 token của một cụm code xuống chỉ còn ~500 token đại diện cấu trúc Graph tĩnh. Token trống sẽ dành cho não AI tư duy logic logic.

### 2.3. Trực quan Hệ thống (Visual Twin)
Hệ thống nội suy mạng nhện sang Web UI Tĩnh thông qua lệnh `vibecode ui`.
- **Giao diện Hộp (Compound Nodes):** Phân chia vùng Node con dính gọn vào Hộp lớn (Các File).
- **Tính năng cần cập nhật (Live Sync):** Sắp tới, để giảm thao tác quét bằng tay, cần gắn module `watchdog`. Cứ lưu code (Ctrl+S) là sơ đồ trên Browser cập nhật tự động nhờ WebSocket.

---

## 3. Các Tính năng Đạt tầm Master (Bổ sung vào Lộ trình sau)

VibeCode hoàn toàn có thể trang bị thêm 2 Vũ khí Hạng nặng sau để đẩy lùi giới hạn của AI:

### 3.1. Phân Tích Lan Truyền Lỗi (Impact Analysis)
Trước khi lập trình viên yêu cầu AI sinh Code để đè (overwrite) lên hàm `verify()`. VibeCode chạy thuật toán duyệt đỉnh, bắn ra thông báo kẹp vào bối cảnh:
> *"Cảnh báo hệ thống: Việc đổi cấu trúc hàm `verify()` sẽ gây sụp đổ lan truyền sang 4 chức năng Thanh Toán và 1 chức năng Đăng Nhập đang gọi trực tiếp tới nó. Đề nghị AI khi code phải viết sao cho tương thích ngược (Backward-compatible) với 5 hàm kia!"*

### 3.2. Graph RAG (Truy vấn Ngữ nghĩa trên Không gian Đồ Thị)
Tích hợp một loại cơ sở dữ liệu `VectorDB` nhỏ đi song song với SQLite. 
Khi Dev ra lệnh chat: *"Antigravity, tìm cho tôi đoạn mã nào liên quan tới xử lý hóa đơn, và thêm tính năng xuất PDF vào đó!"*. 
- VibeCode sẽ tự nhúng câu nói thành Vector, dò trúng cái Node tên là `Invoice.create()`. 
- VibeCode tự động kéo nguyên lưới nhện xung quanh cái Node đó tạo thành Context ném ngược lại cho Antigravity. 
- Dev sẽ không cần phải tự mồi file bằng tay nữa!

---

## 4. Tóm lược Lộ trình
- **Đã hoàn thành (GĐ1-5):** AST Parser gốc, SQLite Graph Builder cơ bản, Linker thế hệ 1, Visual UI tĩnh (Compound nodes, Tap & Dim), Slash Commands.
- **Ghi chú (GĐ 6):** Cần lập lệnh triển khai xử lý ngay Lỗi Trùng Tên Hàm (FQDN), Bổ sung Import External Libs và Cơ chế Watchdog Sync.
