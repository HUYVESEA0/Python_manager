@echo off
title Python Manager - Flask Development Server

REM Kiểm tra môi trường venv
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM Cài đặt packages nếu cần
if not exist venv\Lib\site-packages\flask (
    echo Installing required packages...
    pip install -r requirements_windows.txt
)

REM Khởi chạy Flask
echo Setting Flask environment...
set FLASK_APP=app
set FLASK_DEBUG=1

echo Starting Flask development server...
flask run --host=0.0.0.0 --port=5000

REM Deactivate và thoát
call deactivate
