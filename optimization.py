"""
Tối ưu hóa cho Flask Python Manager trên Windows
"""
from flask import request
from flask_compress import Compress

class AppOptimizer:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
        # 1. Tối ưu cấu hình SQLAlchemy
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # 2. Sử dụng compression để giảm kích thước response
        Compress(app)
        
        # 3. Cấu hình session cho hiệu suất tốt hơn
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = True
        app.config['SESSION_USE_SIGNER'] = True
        
        # 4. Thêm cache headers cho static files
        @app.after_request
        def add_cache_headers(response):
            if '/static/' in request.path:
                # Cache static files trong 30 ngày
                if any(request.path.endswith(ext) for ext in ('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico')):
                    response.cache_control.max_age = 2592000  # 30 days
                    response.cache_control.public = True
            return response
        
        # 5. Cấu hình SQLAlchemy connection pooling
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_recycle': 1800,  # Recycle connections sau 30 phút
        }
        
        return app
