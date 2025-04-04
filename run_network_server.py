"""
Script chạy Flask server trên mạng để có thể truy cập từ các thiết bị khác
"""
import os
import sys
import webbrowser
import threading
import time
from waitress import serve
from app import app

def open_browser(url):
    """Mở trình duyệt web sau một khoảng thời gian ngắn"""
    time.sleep(1.5)  # Đợi server khởi động
    print(f"Opening browser to {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    # Thiết lập Flask để hoạt động trong môi trường phát triển
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['FLASK_ENV'] = 'development'
    
    # Lấy địa chỉ IP của máy tính (nếu được cung cấp qua tham số)
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    open_browser_flag = True if len(sys.argv) <= 3 else sys.argv[3].lower() != 'no-browser'
    
    print(f"\n===== Python Manager Server =====")
    print(f"Starting server on network...")
    print(f"Server addresses:")
    print(f"- Local: http://127.0.0.1:{port}")
    
    # Hiển thị thông tin hữu ích để kết nối từ các thiết bị khác
    actual_ip = None
    if host == '0.0.0.0':
        import socket
        try:
            # Lấy địa chỉ IP thực tế của máy tính
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            actual_ip = s.getsockname()[0]
            s.close()
            print(f"- Network: http://{actual_ip}:{port}")
            print(f"\nShare the Network URL with devices on your local network.")
        except:
            print("Could not determine network IP address.")
    
    # Mở trình duyệt tự động (nếu được yêu cầu)
    if open_browser_flag:
        browser_url = f"http://127.0.0.1:{port}"
        threading.Thread(target=open_browser, args=(browser_url,)).start()
    
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 35 + "\n")
    
    try:
        if os.environ.get('FLASK_DEBUG') == '1':
            # Sử dụng Flask builtin server trong môi trường phát triển
            app.run(host=host, port=port, debug=True, threaded=True)
        else:
            # Sử dụng waitress trong production
            serve(app, host=host, port=port, threads=10)
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"\nError starting server: {e}")
