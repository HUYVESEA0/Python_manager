# Python Manager Deployment Guide

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements_optimized.txt
```

### 2. Cấu hình

- Đảm bảo thiết lập đúng cấu hình trong `config.py`
- Chỉnh sửa `DevelopmentConfig` hoặc `ProductionConfig` tùy theo môi trường

### 3. Khởi chạy cho phát triển

```bash
# Chế độ phát triển
python app.py

# Chế độ tối ưu nhưng vẫn có debug
python run_optimized.py
```

### 4. Khởi chạy cho production

```bash
# Chế độ production
python run_production.py
```

## Tối ưu hóa hiệu suất

### 1. Caching

- Ứng dụng đã được cấu hình với Flask-Caching
- Simple cache được sử dụng mặc định, nhưng có thể chuyển sang Redis trong production

### 2. WSGI Server

- Waitress được sử dụng cho production
- Đã cấu hình connection pooling và thread handling

### 3. Compression

- Flask-Compress đã được cấu hình để nén responses

### 4. Static File Caching

- Static files được cấu hình với cache headers hợp lý

## Tùy chọn nâng cao cho production

### 1. Sử dụng Nginx làm reverse proxy

```nginx
server {
    listen 80;
    server_name pythonmanager.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 30d;
    }
}
```

### 2. Sử dụng Redis cho caching

Trong `app.py`, thay đổi cấu hình cache:

```python
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})
```

### 3. Thiết lập monitoring

Sử dụng các công cụ như Prometheus + Grafana hoặc NewRelic để theo dõi hiệu suất ứng dụng.

### 4. Thiết lập database backup

Đảm bảo thiết lập backup định kỳ cho cơ sở dữ liệu SQLite hoặc chuyển sang PostgreSQL cho môi trường production.
