from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
import datetime
import os
import random
import string
import json
from sqlalchemy import func

# Import models trước khi khởi tạo app
from models import db, User, SystemSetting, ActivityLog, init_app
from models import LabSession, SessionRegistration, LabEntry
from utils import log_activity

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# Cấu hình session để hết hạn sau 30 phút
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

# Khởi tạo database với app
init_app(app)

# Thiết lập Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import thêm decorator mới
from decorators import admin_required, admin_manager_required

# Khởi tạo admin user
def init_admin_user():
    with app.app_context():
        # Check for admin_manager
        admin_manager = User.query.filter_by(role='admin_manager').first()
        if not admin_manager:
            admin_manager = User(
                username='HUYVIESEA',
                email='hhuy0847@gmail.comcom',
                role='admin_manager'
            )
            admin_manager.set_password('huyviesea@manager')
            db.session.add(admin_manager)
            db.session.commit()
            print('Admin Manager created: hhuy0847@gmail.comcom / admin_manager')
            
        # Check for regular admin
        admin = User.query.filter_by(username='HUYVIESEA').first()
        if not admin:
            admin = User(
                username='HUYVIESEA',
                email='hhuy0847@gmail.com',
                role='admin'
            )
            admin.set_password('huyviesea@admin')
            db.session.add(admin)
            db.session.commit()
            print('Admin created: hhuy0847@gmail.com / huyviesea')
        user = User.query.filter_by(username='HUYVIESEA').first()
        if not user:
            user = User(
                username='HUYVIESEA',
                email ='hhuy0847@gmail.com',
                role='user'
            )
            user.set_password('huyviesea@user')
            db.session.add(user)
            db.session.commit()
            print('User created: hhuy0847@gmail.com / huyviesea')
# Gọi hàm khởi tạo admin user
init_admin_user()

from forms import LoginForm, RegistrationForm, UserEditForm, CreateUserForm, SystemSettingsForm
from forms import LabSessionForm, SessionRegistrationForm, LabVerificationForm, LabResultForm

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    # Đếm số lần truy cập trang chủ
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    
    # Lưu thời gian truy cập cuối cùng
    session['last_visit'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    # Tạo cả hai form để sẵn sàng chuyển đổi
    login_form = LoginForm()
    reg_form = RegistrationForm()
    
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            # Tạo session vĩnh viễn nếu remember_me được chọn
            if login_form.remember_me.data:
                session.permanent = True
            
            # Lưu thông tin đăng nhập vào session
            session['user_email'] = user.email
            session['login_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Log the login activity
            log_activity('User login', f'User logged in from {request.remote_addr}', user)
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Email hoặc mật khẩu không đúng', 'danger')
            # Log failed login attempt
            log_activity('Failed login attempt', f'Failed login attempt for email: {login_form.email.data}')
    
    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, form=login_form, register=False, title='Đăng nhập')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    # Tạo cả hai form để sẵn sàng chuyển đổi
    login_form = LoginForm()
    reg_form = RegistrationForm()
    
    if reg_form.validate_on_submit():
        user = User(username=reg_form.username.data, email=reg_form.email.data)
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tài khoản của bạn đã được tạo! Bạn có thể đăng nhập ngay bây giờ', 'success')
        return redirect(url_for('login'))
        
    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, form=reg_form, register=True, title='Đăng ký')

# Route mới để hỗ trợ việc lấy dữ liệu form mới qua AJAX
@app.route('/get-form-data/<form_type>')
def get_form_data(form_type):
    """API để lấy thông tin form cập nhật mà không cần tải lại trang"""
    if form_type == 'login':
        form = LoginForm()
        return {'csrf_token': form.csrf_token._value()}
    elif form_type == 'register':
        form = RegistrationForm()
        return {'csrf_token': form.csrf_token._value()}
    else:
        return {'error': 'Invalid form type'}, 400

@app.route('/logout')
def logout():
    # Log the logout activity
    if current_user.is_authenticated:
        log_activity('User logout', 'User logged out')
    
    # Lưu thời gian đăng xuất trước khi xóa session
    if 'user_email' in session:
        session['logout_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        flash(f'You have been logged out at {session["logout_time"]}', 'info')
    
    logout_user()
    
    # Xóa các session liên quan đến đăng nhập
    session.pop('user_email', None)
    session.pop('login_time', None)
    
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Thêm dữ liệu từ session vào context để hiển thị trong dashboard
    session_data = {
        'visits': session.get('visits', 0),
        'last_visit': session.get('last_visit', 'N/A'),
        'login_time': session.get('login_time', 'N/A')
    }
    return render_template('dashboard.html', session_data=session_data)

@app.route('/session-manager')
@login_required
def session_manager():
    # Hiển thị trang quản lý session
    return render_template('session_manager.html', session=session)

@app.route('/set-session', methods=['POST'])
@login_required
def set_session():
    # Thêm dữ liệu mới vào session
    key = request.form.get('key')
    value = request.form.get('value')
    
    if key and value:
        session[key] = value
        flash(f'Session key "{key}" has been set successfully!', 'success')
    else:
        flash('Both key and value are required', 'danger')
    
    return redirect(url_for('session_manager'))

@app.route('/delete-session/<key>')
@login_required
def delete_session(key):
    # Xóa một key cụ thể khỏi session
    if key in session:
        session.pop(key, None)
        flash(f'Session key "{key}" has been deleted', 'success')
    else:
        flash(f'Session key "{key}" not found', 'danger')
    
    return redirect(url_for('session_manager'))

@app.route('/clear-session')
@login_required
def clear_session():
    # Xóa toàn bộ session trừ các thông tin đăng nhập
    user_email = session.get('user_email')
    login_time = session.get('login_time')
    
    session.clear()
    
    # Giữ lại thông tin đăng nhập
    if user_email:
        session['user_email'] = user_email
    if login_time:
        session['login_time'] = login_time
    
    flash('All session data has been cleared', 'success')
    return redirect(url_for('session_manager'))

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

# Admin user management routes
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {form.username.data} has been created successfully!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/create_user.html', form=form)

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        
        # Check if password change was requested
        if request.form.get('change_password'):
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password and new_password == confirm_password:
                user.set_password(new_password)
            elif new_password:
                flash('Password confirmation does not match!', 'danger')
                return render_template('admin/edit_user.html', form=form, user=user)
        
        db.session.commit()
        flash(f'User {user.username} has been updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    # Pre-populate the form
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/make-admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Only admin_manager can promote to admin
    if not current_user.is_admin_manager() and user.role == 'user':
        flash('Chỉ Admin Manager mới có thể thăng cấp người dùng lên Admin.', 'danger')
        return redirect(url_for('admin_users'))
        
    if user.id != current_user.id:  # Không thay đổi quyền của chính mình
        # Regular admin can only promote to same level
        if current_user.is_admin_manager() or user.role == 'user':
            user.role = 'admin'
            db.session.commit()
            # Log the activity
            log_activity('Make admin', f'User {user.username} (ID: {user.id}) was granted admin privileges')
            flash(f'User {user.username} đã được cấp quyền quản trị!', 'success')
        else:
            flash('Bạn không có quyền thực hiện hành động này.', 'danger')
    else:
        flash('Bạn không thể thay đổi quyền của chính mình!', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/make-admin-manager/<int:user_id>')
@login_required
@admin_manager_required
def make_admin_manager(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:  # Không thay đổi quyền của chính mình
        user.role = 'admin_manager'
        db.session.commit()
        # Log the activity
        log_activity('Make admin manager', f'User {user.username} (ID: {user.id}) was granted admin manager privileges')
        flash(f'User {user.username} đã được cấp quyền quản trị cấp cao!', 'success')
    else:
        flash('Bạn không thể thay đổi quyền của chính mình!', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/remove-admin/<int:user_id>')
@login_required
@admin_required
def remove_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Only admin_manager can demote another admin_manager
    if user.role == 'admin_manager' and not current_user.is_admin_manager():
        flash('Chỉ Admin Manager mới có thể hạ cấp một Admin Manager khác.', 'danger')
        return redirect(url_for('admin_users'))
    
    if user.id != current_user.id:  # Không thay đổi quyền của chính mình
        user.role = 'user'
        db.session.commit()
        flash(f'Quyền quản trị của {user.username} đã bị gỡ bỏ!', 'success')
    else:
        flash('Bạn không thể thay đổi quyền của chính mình!', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:  # Không xóa chính mình
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} đã bị xóa!', 'success')
    else:
        flash('Bạn không thể xóa tài khoản của chính mình!', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/get-form/<form_type>')
def get_form(form_type):
    """Route để lấy form qua AJAX mà không cần tải lại trang"""
    if form_type == 'login':
        form = LoginForm()
        return render_template('partials/login_form.html', form=form)
    elif form_type == 'register':
        form = RegistrationForm()
        return render_template('partials/register_form.html', form=form)
    else:
        return '', 404

# System Settings routes
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    # Initialize default settings if they don't exist
    if SystemSetting.query.count() == 0:
        SystemSetting.set_setting('app_name', 'Python Manager', 'string', 'Application Name')
        SystemSetting.set_setting('app_description', 'A Flask application for managing Python projects', 'string', 'Application Description')
        SystemSetting.set_setting('enable_registration', True, 'boolean', 'Enable User Registration')
        SystemSetting.set_setting('enable_password_reset', True, 'boolean', 'Enable Password Reset')
        SystemSetting.set_setting('items_per_page', 25, 'integer', 'Number of items per page in listings')
    
    form = SystemSettingsForm()
    
    # If form is submitted and valid
    if form.validate_on_submit():
        SystemSetting.set_setting('app_name', form.app_name.data, 'string', 'Application Name')
        SystemSetting.set_setting('app_description', form.app_description.data, 'string', 'Application Description')
        SystemSetting.set_setting('enable_registration', form.enable_registration.data, 'boolean', 'Enable User Registration')
        SystemSetting.set_setting('enable_password_reset', form.enable_password_reset.data, 'boolean', 'Enable Password Reset')
        SystemSetting.set_setting('items_per_page', form.items_per_page.data, 'integer', 'Number of items per page in listings')
        
        db.session.commit()
        flash('System settings have been updated successfully!', 'success')
        return redirect(url_for('system_settings'))
    
    # Pre-populate form with current settings
    form.app_name.data = SystemSetting.get_setting('app_name', 'Python Manager')
    form.app_description.data = SystemSetting.get_setting('app_description', 'A Flask application for managing Python projects')
    form.enable_registration.data = SystemSetting.get_setting('enable_registration', True)
    form.enable_password_reset.data = SystemSetting.get_setting('enable_password_reset', True)
    form.items_per_page.data = SystemSetting.get_setting('items_per_page', 25)
    
    # Get all settings for display
    settings = SystemSetting.query.all()
    
    return render_template('admin/system_settings.html', form=form, settings=settings)

@app.route('/admin/settings/reset')
@login_required
@admin_required
def reset_settings():
    # Delete all settings and recreate defaults
    SystemSetting.query.delete()
    db.session.commit()
    
    # Redirect to settings page which will recreate defaults
    flash('System settings have been reset to defaults!', 'success')
    return redirect(url_for('system_settings'))

# Add these new routes for activity logs
@app.route('/admin/logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    per_page = int(SystemSetting.get_setting('items_per_page', 25))
    
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return render_template('admin/logs.html', logs=logs)

@app.route('/admin/logs/clear', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    if request.form.get('confirm') == 'yes':
        # Log that logs are being cleared before actually clearing them
        log_activity('Clear all logs', 'All activity logs were cleared from the system')
        
        # Delete all logs except the one we just created
        last_log = ActivityLog.query.order_by(ActivityLog.id.desc()).first()
        
        if last_log:
            ActivityLog.query.filter(ActivityLog.id != last_log.id).delete()
        else:
            ActivityLog.query.delete()
            
        db.session.commit()
        flash('All activity logs have been cleared', 'success')
    else:
        flash('Confirmation required to clear logs', 'danger')
        
    return redirect(url_for('activity_logs'))

# Add an admin manager only route
@app.route('/admin/system-operations')
@login_required
@admin_manager_required
def system_operations():
    """Advanced system operations only available to admin manager"""
    return render_template('admin/system_operations.html')

# Add the search route
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        flash('Please enter at least 2 characters for search', 'warning')
        return redirect(url_for('index'))
    
    # Search in users
    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) | 
        (User.email.ilike(f'%{query}%'))
    ).all()
    
    # Search in activity logs (for admins only)
    activities = []
    if current_user.is_authenticated and current_user.is_admin():
        activities = ActivityLog.query.filter(
            (ActivityLog.action.ilike(f'%{query}%')) | 
            (ActivityLog.details.ilike(f'%{query}%'))
        ).limit(25).all()
    
    # Search in system settings (for admins only)
    settings = []
    if current_user.is_authenticated and current_user.is_admin():
        settings = SystemSetting.query.filter(
            (SystemSetting.key.ilike(f'%{query}%')) | 
            (SystemSetting.value.ilike(f'%{query}%')) |
            (SystemSetting.description.ilike(f'%{query}%'))
        ).all()
    
    # Log the search activity
    if current_user.is_authenticated:
        log_activity('Search', f'User searched for: {query}')
    
    # Check if any results were found
    results_found = bool(users or activities or settings)
    
    return render_template('search_results.html', 
                          query=query, 
                          users=users,
                          activities=activities,
                          settings=settings,
                          results_found=results_found)

# Lab Session routes for students
@app.route('/lab-sessions')
@login_required
def lab_sessions():
    """View available lab sessions for registration"""
    # Show only future, active sessions that are not full
    now = datetime.datetime.now()
    available_sessions = LabSession.query.filter(
        LabSession.is_active == True,
        LabSession.date >= now.date(),
        LabSession.start_time > now
    ).order_by(LabSession.date, LabSession.start_time).all()
    
    registered_sessions = LabSession.query.join(SessionRegistration).filter(
        SessionRegistration.student_id == current_user.id
    ).order_by(LabSession.date, LabSession.start_time).all()
    
    return render_template('lab/lab_sessions.html', 
                           available_sessions=available_sessions,
                           registered_sessions=registered_sessions)

@app.route('/register-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def register_lab_session(session_id):
    """Register for a lab session"""
    lab_session = LabSession.query.get_or_404(session_id)
    
    # Check if session is available
    if not lab_session.can_register():
        flash('Ca thực hành này không khả dụng cho đăng ký.', 'danger')
        return redirect(url_for('lab_sessions'))
    
    # Check if already registered
    existing_reg = SessionRegistration.query.filter_by(
        student_id=current_user.id, session_id=session_id
    ).first()
    
    if existing_reg:
        flash('Bạn đã đăng ký ca thực hành này.', 'warning')
        return redirect(url_for('lab_sessions'))
    
    form = SessionRegistrationForm()
    form.session_id.data = session_id
    
    if form.validate_on_submit():
        registration = SessionRegistration(
            student_id=current_user.id,
            session_id=session_id,
            notes=form.notes.data
        )
        db.session.add(registration)
        db.session.commit()
        
        log_activity('Lab registration', f'Registered for lab session {lab_session.title}')
        flash('Đăng ký ca thực hành thành công!', 'success')
        return redirect(url_for('lab_sessions'))
    
    return render_template('lab/register_session.html', form=form, session=lab_session)

@app.route('/my-lab-sessions')
@login_required
def my_lab_sessions():
    """View registered lab sessions"""
    registered_sessions = LabSession.query.join(SessionRegistration).filter(
        SessionRegistration.student_id == current_user.id
    ).order_by(LabSession.date, LabSession.start_time).all()
    
    # Get lab entries history
    lab_history = LabEntry.query.filter_by(
        student_id=current_user.id
    ).order_by(LabEntry.check_in_time.desc()).all()
    
    return render_template('lab/my_sessions.html', 
                           sessions=registered_sessions,
                           lab_history=lab_history)

@app.route('/verify-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def verify_lab_session(session_id):
    """Verify and check in to a lab session"""
    lab_session = LabSession.query.get_or_404(session_id)
    
    # Check if registered
    registration = SessionRegistration.query.filter_by(
        student_id=current_user.id, session_id=session_id
    ).first_or_404()
    
    # Check if session is in progress
    if not lab_session.is_in_progress():
        flash('Ca thực hành này hiện không diễn ra.', 'danger')
        return redirect(url_for('my_lab_sessions'))
    
    # Check if already checked in
    existing_entry = LabEntry.query.filter_by(
        student_id=current_user.id, 
        session_id=session_id,
        check_out_time=None
    ).first()
    
    if existing_entry:
        return redirect(url_for('lab_session_active', entry_id=existing_entry.id))
    
    form = LabVerificationForm()
    
    if form.validate_on_submit():
        if form.verification_code.data == lab_session.verification_code:
            # Create lab entry
            entry = LabEntry(
                student_id=current_user.id,
                session_id=session_id
            )
            db.session.add(entry)
            
            # Update registration status
            registration.attendance_status = 'attended'
            
            db.session.commit()
            
            log_activity('Lab check-in', f'Checked in to lab session {lab_session.title}')
            flash('Xác thực thành công! Bạn đã bắt đầu ca thực hành.', 'success')
            return redirect(url_for('lab_session_active', entry_id=entry.id))
        else:
            flash('Mã xác thực không đúng.', 'danger')
    
    return render_template('lab/verify_session.html', form=form, session=lab_session)

@app.route('/lab-session-active/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def lab_session_active(entry_id):
    """Active lab session with timer and result submission"""
    entry = LabEntry.query.filter_by(
        id=entry_id, student_id=current_user.id
    ).first_or_404()
    
    lab_session = entry.session
    
    # Check if already checked out
    if entry.check_out_time:
        flash('Ca thực hành này đã kết thúc.', 'info')
        return redirect(url_for('my_lab_sessions'))
    
    form = LabResultForm()
    
    if form.validate_on_submit():
        entry.lab_result = form.lab_result.data
        entry.check_out_time = datetime.datetime.now()
        db.session.commit()
        
        log_activity('Lab check-out', f'Completed lab session {lab_session.title}')
        flash('Bạn đã nộp kết quả và kết thúc ca thực hành!', 'success')
        return redirect(url_for('my_lab_sessions'))
    
    # Calculate time remaining
    now = datetime.datetime.now()
    time_elapsed = now - entry.check_in_time
    time_remaining = lab_session.end_time - now if now < lab_session.end_time else datetime.timedelta(0)
    
    return render_template('lab/active_session.html', 
                           entry=entry, 
                           session=lab_session,
                           form=form,
                           time_elapsed=time_elapsed,
                           time_remaining=time_remaining)

# Teacher routes for lab management
@app.route('/admin/lab-sessions')
@login_required
@admin_required
def admin_lab_sessions():
    """Manage lab sessions for teachers"""
    lab_sessions = LabSession.query.order_by(LabSession.date.desc(), LabSession.start_time).all()
    return render_template('admin/lab_sessions.html', sessions=lab_sessions)

@app.route('/admin/create-lab-session', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lab_session():
    """Create a new lab session"""
    form = LabSessionForm()
    
    if form.validate_on_submit():
        # Generate a verification code if not provided
        verification_code = form.verification_code.data
        if not verification_code:
            verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Convert form times to datetime
        start_datetime = datetime.datetime.combine(form.date.data, form.start_time.data)
        end_datetime = datetime.datetime.combine(form.date.data, form.end_time.data)
        
        lab_session = LabSession(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            start_time=start_datetime,
            end_time=end_datetime,
            location=form.location.data,
            max_students=form.max_students.data,
            is_active=form.is_active.data,
            verification_code=verification_code,
            created_by=current_user.id
        )
        
        db.session.add(lab_session)
        db.session.commit()
        
        log_activity('Create lab session', f'Created lab session: {form.title.data}')
        flash(f'Ca thực hành "{form.title.data}" đã được tạo thành công! Mã xác thực: {verification_code}', 'success')
        return redirect(url_for('admin_lab_sessions'))
    
    return render_template('admin/create_lab_session.html', form=form)

@app.route('/admin/edit-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lab_session(session_id):
    """Edit an existing lab session"""
    lab_session = LabSession.query.get_or_404(session_id)
    form = LabSessionForm()
    
    if form.validate_on_submit():
        # Convert form times to datetime
        start_datetime = datetime.datetime.combine(form.date.data, form.start_time.data)
        end_datetime = datetime.datetime.combine(form.date.data, form.end_time.data)
        
        lab_session.title = form.title.data
        lab_session.description = form.description.data
        lab_session.date = form.date.data
        lab_session.start_time = start_datetime
        lab_session.end_time = end_datetime
        lab_session.location = form.location.data
        lab_session.max_students = form.max_students.data
        lab_session.is_active = form.is_active.data
        
        # Update verification code if provided
        if form.verification_code.data:
            lab_session.verification_code = form.verification_code.data
        
        db.session.commit()
        
        log_activity('Edit lab session', f'Updated lab session: {lab_session.title}')
        flash(f'Ca thực hành "{lab_session.title}" đã được cập nhật!', 'success')
        return redirect(url_for('admin_lab_sessions'))
    
    # Pre-populate form
    form.title.data = lab_session.title
    form.description.data = lab_session.description
    form.date.data = lab_session.date
    form.start_time.data = lab_session.start_time.time()
    form.end_time.data = lab_session.end_time.time()
    form.location.data = lab_session.location
    form.max_students.data = lab_session.max_students
    form.is_active.data = lab_session.is_active
    form.verification_code.data = lab_session.verification_code
    
    return render_template('admin/edit_lab_session.html', form=form, session=lab_session)

@app.route('/admin/lab-session-attendees/<int:session_id>')
@login_required
@admin_required
def lab_session_attendees(session_id):
    """View students registered for a lab session"""
    lab_session = LabSession.query.get_or_404(session_id)
    
    registrations = SessionRegistration.query.filter_by(
        session_id=session_id
    ).join(User).order_by(User.username).all()
    
    # Get entries for this session
    entries = LabEntry.query.filter_by(
        session_id=session_id
    ).join(User).order_by(LabEntry.check_in_time).all()
    
    return render_template('admin/session_attendees.html', 
                           session=lab_session,
                           registrations=registrations,
                           entries=entries)

# Admin manager routes for scheduling
@app.route('/admin/schedule-lab-sessions')
@login_required
@admin_manager_required
def schedule_lab_sessions():
    """Schedule lab sessions with minimum student requirements"""
    # Get sessions with at least 5 registrations
    valid_sessions = db.session.query(
        LabSession, func.count(SessionRegistration.id).label('student_count')
    ).join(SessionRegistration).group_by(LabSession.id).having(
        func.count(SessionRegistration.id) >= 5
    ).order_by(LabSession.date, LabSession.start_time).all()
    
    # Get sessions with less than 5 registrations
    pending_sessions = db.session.query(
        LabSession, func.count(SessionRegistration.id).label('student_count')
    ).join(SessionRegistration).group_by(LabSession.id).having(
        func.count(SessionRegistration.id) < 5
    ).order_by(LabSession.date, LabSession.start_time).all()
    
    return render_template('admin/schedule_sessions.html', 
                           valid_sessions=valid_sessions,
                           pending_sessions=pending_sessions)

from forms import CourseForm, LessonForm
from models import Course, Lesson, Enrollment

@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:course_id>')
def course(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course.html', course=course)

@app.route('/course/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(title=form.title.data, description=form.description.data)
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('courses'))
    return render_template('create_course.html', form=form)

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm()
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course', course_id=course.id))
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
    return render_template('create_course.html', form=form)

@app.route('/course/<int:course_id>/lesson/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_lesson(course_id):
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(title=form.title.data, content=form.content.data, course_id=course_id)
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('course', course_id=course_id))
    return render_template('create_lesson.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)