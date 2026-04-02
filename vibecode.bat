@echo off
:: ================================================
:: VibeCode OS Wrapper
:: Giúp người dùng thực thi lệnh không cần gõ dài dòng
:: Cú pháp: 
:: vibecode.bat scan
:: vibecode.bat ui
:: vibecode.bat context <file>
:: ================================================

IF "%1"=="" (
    echo [LOI] Vui long nhap it nhat 1 lenh. (Vi du: vibecode.bat scan)
    exit /b 1
)

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [LOI] Khong tim thay Python tai .venv. Ban da chay install.bat chua?
    exit /b 1
)

:: Goi lenh truyen truc tiep cac doi so (*) sang cli python
.\.venv\Scripts\python -m vibecode %*
