@echo off
echo Python Manager - Development Server Launcher

REM Đường dẫn đến thư mục venv
SET VENV_DIR=venv

REM Kiểm tra xem thư mục venv có tồn tại không
if not exist %VENV_DIR% (
    echo Virtual environment not found. Creating new one...
    python -m venv %VENV_DIR%
    
    REM Nếu không thành công, thử với Python3
    if errorlevel 1 (
        echo Trying with python3 command...
        python3 -m venv %VENV_DIR%
    )
    
    if not exist %VENV_DIR% (
        echo ERROR: Could not create virtual environment!
        echo Please create it manually with: python -m venv venv
        pause
        exit /b 1
    )
)

REM Kích hoạt môi trường ảo và chạy Flask
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

echo.
echo === Virtual environment activated ===
echo Installing dependencies...
pip install -r requirements_windows.txt

echo.
echo === Dependencies installed ===
echo Setting Flask environment variables...
set FLASK_APP=app
set FLASK_DEBUG=1

echo.
echo === Starting Flask development server ===
echo Press Ctrl+C to stop the server when finished.
echo.
flask run --host=0.0.0.0 --port=5000

REM Giữ cửa sổ mở sau khi kết thúc
echo.
echo Server has stopped. Press any key to exit...
pause > nul
