"""
Tối ưu hóa cho Flask Python Manager
"""

from flask import request

def configure_optimization(app):
    """
    Cấu hình các tối ưu hóa cho Flask app
    """
    # 1. Compression (gzip)
    from flask_compress import Compress
    Compress(app)
    
    # 2. Tối ưu caching headers cho static files
    @app.after_request
    def add_cache_headers(response):
        # Chỉ thêm cache headers cho static files
        if '/static/' in request.path:
            # Cache assets for 1 year (Tối đa như RFC 2616 đề xuất)
            if any(request.path.endswith(ext) for ext in ('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico')):
                response.cache_control.max_age = 31536000  # 1 year in seconds
                response.cache_control.public = True
        return response
    
    # 3. Tối ưu SQL Alchemy
    app.config['SQLALCHEMY_ECHO'] = False  # Tắt SQL logging trên production
    
    # 4. Sử dụng uwsgi nếu có thể
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
    except ImportError:
        pass
    
    return app
