# Hướng dẫn sử dụng môi trường ảo (venv) với Python Manager

## Cài đặt môi trường ảo

```bash
# Tạo môi trường ảo mới
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows (Command Prompt):
venv\Scripts\activate
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Trên MacOS/Linux:
source venv/bin/activate
```

## Cài đặt dependencies

```bash
# Sau khi kích hoạt venv
pip install -r requirements_windows.txt
```

## Chạy ứng dụng

### Cách 1: Sử dụng Flask CLI

```bash
# Sau khi kích hoạt venv
set FLASK_APP=app
set FLASK_DEBUG=1
flask run
```

### Cách 2: Sử dụng file batch có sẵn

```bash
# Chạy file batch để tự động kích hoạt venv và khởi động Flask
activate_and_run.bat
```

### Cách 3: Chạy trực tiếp từ Python

```bash
# Sau khi kích hoạt venv
python app.py
```

## Gỡ bỏ kích hoạt venv

```bash
# Khi hoàn tất công việc
deactivate
```

## Lưu ý quan trọng

1. Luôn đảm bảo môi trường ảo được kích hoạt trước khi cài đặt packages hoặc chạy ứng dụng
2. Terminal hoặc Command Prompt sẽ hiển thị `(venv)` ở đầu dòng khi venv được kích hoạt
3. Nếu bạn mở terminal mới, bạn cần kích hoạt lại venv
