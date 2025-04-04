"""
Script khởi chạy Python Manager với tối ưu hiệu suất trên Windows
"""
from waitress import serve
from app import app

if __name__ == '__main__':
    print("Khởi chạy Python Manager với Waitress WSGI server...")
    print("Ứng dụng có thể truy cập tại: http://localhost:8080")
    
    # Khởi chạy với waitress thay vì development server
    serve(app, host='0.0.0.0', port=8080, threads=4)
