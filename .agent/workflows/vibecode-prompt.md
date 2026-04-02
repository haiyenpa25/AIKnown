---
description: Lấy Ngữ cảnh File và sinh Giao thức Lệnh chống Ảo giác (Hallucination) cho AI.
---

1. Trong câu hỏi của lập trình viên, hãy bóc tách ra <Mục_Tiêu_Của_Họ> và <Tên_File_Họ_Muốn>. (Ví dụ: "thêm tính năng auth vào src/main.py").
2. Sử dụng công cụ `run_command` thực thi script tự động hóa:
```bash
.\vibecode.bat prompt "<Mục_Tiêu_Của_Họ>" <Tên_File_Họ_Muốn>
```
3. Sau khi lệnh thực thi thành công, nó sẽ sinh ra một tệp `AI_PROMPT_TO_COPY.txt`. Bạn HÃY sử dụng công cụ `view_file` (hoặc `cat`) để ĐỌC nội dung file này.
4. TOÀN BỘ NỘI DUNG TỪ FILE ĐÓ sẽ trở thành **Nhận thức Ngữ Cảnh Bắt Buộc (Required Context)** của bạn trong phiên làm việc này. Hãy tự dặn bản thân tuân thủ nghiêm ngặt 3 MỆNH LỆNH CHỐNG ẢO GIÁC được ghi ở cuối tệp. Tuyệt đối không được đoán mò logic các hàm `Outbound`.
5. Tiếp tục phân tích yêu cầu của lập trình viên dựa theo cấu trúc Graph bạn vừa đọc được. Đưa ra tư vấn hợp lý và chính xác nhất cho người dùng! 
