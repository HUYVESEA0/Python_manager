"""
Script khởi chạy Python Manager với cấu hình production
"""
from waitress import serve
from app import app
import logging
from logging.handlers import RotatingFileHandler
import os

if __name__ == '__main__':
    # Thiết lập logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Cấu hình logging với rotation để không chiếm quá nhiều ổ đĩa
    file_handler = RotatingFileHandler('logs/python_manager.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Thêm handler vào app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Python Manager startup')
    
    # Thay đổi cấu hình để sử dụng cho production
    app.config.from_object('config.ProductionConfig')
    
    # Vô hiệu hóa debug mode
    app.debug = False
    
    print("Starting Python Manager in production mode...")
    print("Application can be accessed at: http://localhost:8080")
    
    # Khởi chạy ứng dụng với waitress WSGI server (phù hợp cho Windows)
    serve(app, host='0.0.0.0', port=8080, threads=8, url_scheme='http')
