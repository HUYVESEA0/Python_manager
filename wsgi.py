"""
WSGI entry point for Python Manager application
Có thể chạy trực tiếp hoặc qua WSGI server như gunicorn/uwsgi
"""
import sys
import os

# Thêm thư mục hiện tại vào path để đảm bảo import hoạt động đúng trong venv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application

# Cho phép chạy trực tiếp file này
if __name__ == "__main__":
    # Kiểm tra xem đang chạy trong venv không
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Running in virtual environment:", sys.prefix)
    else:
        print("WARNING: Not running in a virtual environment!")
        
    # Chạy Flask development server
    application.run(debug=True, host='0.0.0.0', port=5000)
