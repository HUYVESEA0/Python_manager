@echo off
title Python Manager Server
color 0A
cls

echo ===== Python Manager Server =====
echo.
echo Chọn cách thức khởi động:
echo 1. Khởi động cho mạng nội bộ (mở trình duyệt)
echo 2. Khởi động tại localhost (mở trình duyệt)
echo 3. Khởi động cho mạng nội bộ (không mở trình duyệt)
echo 4. Thay đổi cổng (mặc định: 5000)
echo 5. Thoát
echo.

set /p option=Nhập lựa chọn (1-5): 

if "%option%"=="1" (
    cls
    echo Khởi động server trên mạng và mở trình duyệt...
    python run_network_server.py
) else if "%option%"=="2" (
    cls
    echo Khởi động server tại localhost và mở trình duyệt...
    python run_network_server.py 127.0.0.1
) else if "%option%"=="3" (
    cls
    echo Khởi động server trên mạng (không mở trình duyệt)...
    python run_network_server.py 0.0.0.0 5000 no-browser
) else if "%option%"=="4" (
    set /p port=Nhập cổng (số nguyên từ 1024-65535): 
    cls
    echo Khởi động server trên cổng %port%...
    python run_network_server.py 0.0.0.0 %port%
) else if "%option%"=="5" (
    echo Thoát chương trình...
    exit /b
) else (
    echo Lựa chọn không hợp lệ!
    pause
    cls
    call %0
)

pause
