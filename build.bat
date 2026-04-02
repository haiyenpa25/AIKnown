@echo off
echo ===================================================
echo VibeCode PyInstaller Build Script
echo ===================================================

echo Kich hoat moi truong .venv...
call .venv\Scripts\activate.bat

echo Kiem tra / Cai dat PyInstaller...
pip install pyinstaller

echo Dang bien dich VibeCode thanh file .exe...
echo.
pyinstaller --onefile ^
  --name vibecode ^
  --collect-all tree_sitter_python ^
  --collect-all tree_sitter_php ^
  --collect-all tree_sitter_javascript ^
  vibecode\__main__.py

echo.
echo ===================================================
echo [SUCCESS] Build hoan tat! File vibecode.exe nam trong thu muc 'dist\'.
echo ===================================================
pause
