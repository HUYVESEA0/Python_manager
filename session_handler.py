"""
Module quản lý session tự động, đảm bảo tính nhất quán và giải quyết 
các vấn đề phổ biến với session trong Flask
"""
from flask import session, g, request
from flask_login import current_user
import datetime
import functools

class SessionHandler:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Khởi tạo session handler với Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Đăng ký hàm xử lý lỗi session
        @app.errorhandler(500)
        def handle_session_error(e):
            if 'session' in str(e):
                session.clear()
                return "Session error - cleared cookies. Please try again.", 500
            return e
    
    def before_request(self):
        """Xử lý trước mỗi request"""
        # Đặt thời gian bắt đầu request (để tính toán thời gian phản hồi)
        g.request_start_time = datetime.datetime.now()
        
        # Đánh dấu session đã được truy cập (để refresh thời gian hết hạn)
        session.modified = True
        
        # Kiểm tra tính nhất quán của session với trạng thái đăng nhập
        self._ensure_session_consistency()
    
    def after_request(self, response):
        """Xử lý sau mỗi request"""
        # Thêm thời gian phản hồi vào header (để debug)
        response_time = datetime.datetime.now() - g.request_start_time
        response.headers['X-Response-Time'] = str(response_time.total_seconds())
        
        return response
    
    def _ensure_session_consistency(self):
        """Đảm bảo session phù hợp với trạng thái đăng nhập hiện tại"""
        # Đã đăng nhập nhưng không có thông tin session
        if current_user.is_authenticated and 'user_email' not in session:
            session['user_email'] = current_user.email
            session['login_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Chưa đăng nhập nhưng session vẫn còn thông tin user
        if not current_user.is_authenticated and 'user_email' in session:
            # Giữ lại một số session key quan trọng
            keep_keys = ['visits', 'last_visit', 'csrf_token']
            preserved_values = {k: session[k] for k in keep_keys if k in session}
            
            # Xóa session liên quan đến authentication
            auth_keys = ['user_email', 'login_time', 'logout_time']
            for key in list(session.keys()):
                if key in auth_keys:
                    session.pop(key, None)
            
            # Khôi phục các giá trị cần giữ lại
            for k, v in preserved_values.items():
                session[k] = v


def login_required_with_redirect(view_func):
    """Decorator mở rộng login_required, lưu URL hiện tại để chuyển hướng sau đăng nhập"""
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Lưu URL hiện tại vào session để chuyển hướng sau khi đăng nhập
            session['next_url'] = request.url
            from flask import redirect, url_for, flash
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view
