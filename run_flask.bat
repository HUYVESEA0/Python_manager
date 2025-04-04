@echo off
echo Checking virtual environment...

REM Kiểm tra xem đang trong môi trường ảo chưa
if not defined VIRTUAL_ENV (
    echo WARNING: Virtual environment is not activated!
    echo Please activate your virtual environment first with:
    echo.
    if exist venv (
        echo     venv\Scripts\activate
    ) else if exist .venv (
        echo     .venv\Scripts\activate
    ) else (
        echo     [path-to-your-venv]\Scripts\activate
    )
    echo.
    echo Press any key to try continuing anyway...
    pause > nul
)

echo Installing required packages...
pip install -r requirements_windows.txt

echo Setting environment variables...
set FLASK_APP=app
set FLASK_DEBUG=1

echo Starting Flask development server...
flask run --host=0.0.0.0 --port=5000
pause
