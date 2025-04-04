@echo off
title Python Manager App
echo Starting Python Manager Application...
echo.

REM Kiểm tra xem có giao diện đồ họa hay không
if "%1"=="nogui" goto start_simple

REM Thử chạy GUI launcher
python server_launcher.py
if %errorlevel% equ 0 goto end

:start_simple
echo GUI không khả dụng, chạy chế độ dòng lệnh...
python run_network_server.py

:end
