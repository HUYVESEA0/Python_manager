"""
Tối ưu hóa cho Flask Python Manager trên Windows
"""
from flask import request, g
import time
import logging

logger = logging.getLogger(__name__)

def configure_windows_optimization(app):
    """Cấu hình tối ưu cho Windows"""
    
    # 1. Request timing middleware để theo dõi thời gian xử lý request
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            # Log các request chậm (> 500ms)
            if elapsed > 0.5:
                logger.warning(f'Slow request: {request.path} took {elapsed:.2f}s')
            # Thêm header để theo dõi hiệu suất
            response.headers['X-Response-Time'] = f'{elapsed:.4f}s'
        return response
    
    # 2. Cache các static files
    @app.after_request
    def add_cache_headers(response):
        if '/static/' in request.path:
            # Thiết lập cache tùy thuộc vào loại file
            if any(request.path.endswith(ext) for ext in ('.css', '.js')):
                # Cache CSS/JS trong 7 ngày
                response.cache_control.max_age = 604800
                response.cache_control.public = True
            elif any(request.path.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.ico')):
                # Cache images trong 30 ngày
                response.cache_control.max_age = 2592000
                response.cache_control.public = True
        return response
    
    # 3. Thiết lập connection pooling cho Windows
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,  # Số lượng connections trong pool
        'max_overflow': 10,  # Số lượng connections có thể tạo thêm khi pool đầy
        'pool_timeout': 30,  # Timeout khi lấy connection từ pool
        'pool_recycle': 1800,  # Recycle connection sau 30 phút
    }
    
    # 4. Thiết lập các tùy chọn Waitress
    app.config['WAITRESS_OPTIONS'] = {
        'threads': 4,  # Số lượng threads
        'backlog': 100,  # Số lượng requests có thể chờ trong queue
        'connection_limit': 1000,  # Số lượng kết nối tối đa
        'cleanup_interval': 30,  # Dọn dẹp connections không hoạt động
    }
    
    return app
