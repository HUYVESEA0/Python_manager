from models import ActivityLog, db
from flask_login import current_user
from flask import request

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
