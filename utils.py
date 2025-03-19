from flask import request
from flask_login import current_user
from models import db, ActivityLog

def log_activity(action, details=None, user=None):
    """
    Log user activity
    
    :param action: Description of the action performed
    :param details: Additional details about the action (optional)
    :param user: User who performed the action (defaults to current_user)
    """
    if user is None:
        user = current_user if current_user.is_authenticated else None
    
    log_entry = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        details=details,
        ip_address=request.remote_addr
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return log_entry
