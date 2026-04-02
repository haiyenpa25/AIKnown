@echo off
echo ===================================================
echo VibeCode Installer - AI Context Environment Setup
echo ===================================================

:: Kiểm tra Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Python chua duoc cai dat (hoac chua nam trong PATH).
    echo Vui long truy cap https://www.python.org/downloads/ de tai Python 3.10+
    echo Dong thoi hay NHO TICK chon "Add Python to PATH" o man hinh cai dat!
    pause
    exit /b 1
)

echo [OK] Da tim thay Python.
echo Dang khoi tao moi truong ao (.venv)...
python -m venv .venv

echo Dang tai va cai dat thu vien cho VibeCode (tu requirements.txt)...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

echo ===================================================
echo [SUCCESS] Hoan tat cai dat VibeCode!
echo Ban co the chay VibeCode qua lenh:
echo .venv\Scripts\python -m vibecode
echo ===================================================
pause
