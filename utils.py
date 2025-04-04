from models import ActivityLog, db
from flask_login import current_user
from flask import request, session
import datetime

def log_activity(action, details, user=None):
    if user is None:
        user = current_user if current_user.is_authenticated else None
    
    log = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

def ensure_session_consistency():
    """Kiểm tra và đảm bảo tính nhất quán của session"""
    # Nếu người dùng đăng nhập nhưng session không có email người dùng
    if current_user.is_authenticated and 'user_email' not in session:
        session['user_email'] = current_user.email
        session['login_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Nếu người dùng không đăng nhập nhưng session vẫn còn thông tin user
    if not current_user.is_authenticated and 'user_email' in session:
        session.pop('user_email', None)
        session.pop('login_time', None)

def clear_auth_session():
    """Xóa các session liên quan đến xác thực"""
    auth_keys = ['user_email', 'login_time', 'logout_time', '_flashes']
    for key in list(session.keys()):
        if key in auth_keys:
            session.pop(key, None)
