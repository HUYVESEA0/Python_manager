from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# Thay thế url_parse bằng url_helpers.url_parse để tương thích hơn
from werkzeug.urls import url_parse
import datetime
import os

# Import models trước khi khởi tạo app
from models import db, User, SystemSetting, ActivityLog, init_app
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

# Khởi tạo admin user
def init_admin_user():
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='HUYVIESEA',
                email='hhuy0847@gmail.com',
                role='admin'
            )
            admin.set_password('huyviesea')
            db.session.add(admin)
            db.session.commit()
            print('Admin created: hhuy0847@gmail.com / huyviesea')

# Gọi hàm khởi tạo admin user
init_admin_user()

from forms import LoginForm, RegistrationForm, UserEditForm, CreateUserForm, SystemSettingsForm
from decorators import admin_required

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
    if user.id != current_user.id:  # Không thay đổi quyền của chính mình
        user.role = 'admin'
        db.session.commit()
        # Log the activity
        log_activity('Make admin', f'User {user.username} (ID: {user.id}) was granted admin privileges')
        flash(f'User {user.username} đã được cấp quyền quản trị!', 'success')
    else:
        flash('Bạn không thể thay đổi quyền của chính mình!', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/remove-admin/<int:user_id>')
@login_required
@admin_required
def remove_admin(user_id):
    user = User.query.get_or_404(user_id)
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

if __name__ == '__main__':
    app.run(debug=True)