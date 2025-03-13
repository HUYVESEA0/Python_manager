from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# Thay thế url_parse bằng url_helpers.url_parse để tương thích hơn
from werkzeug.urls import url_parse
import datetime
import os

# Import models trước khi khởi tạo app
from models import db, User, init_app

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

from forms import LoginForm, RegistrationForm
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
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Email hoặc mật khẩu không đúng', 'danger')
    
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

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/make-admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:  # Không thay đổi quyền của chính mình
        user.role = 'admin'
        db.session.commit()
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

@app.before_first_request
def create_tables():
    # Tạo admin mặc định nếu không có
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin1234')
        db.session.add(admin)
        db.session.commit()
        print('Admin created: admin@example.com / admin1234')

if __name__ == '__main__':
    app.run(debug=True)