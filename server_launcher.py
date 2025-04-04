"""
Ứng dụng GUI để khởi động Python Manager Server
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import socket
import webbrowser
import time

class ServerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Manager - Server Launcher")
        self.root.geometry("650x450")
        self.root.resizable(False, False)
        
        # Đặt icon nếu có
        try:
            self.root.iconbitmap("static/favicon.ico")
        except:
            pass
        
        # Biến lưu trạng thái
        self.server_process = None
        self.is_running = False
        self.port = tk.StringVar(value="5000")
        self.host = tk.StringVar(value="0.0.0.0")
        self.open_browser = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11))
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TCheckbutton", font=("Arial", 11))
        style.configure("TRadiobutton", font=("Arial", 11))
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Python Manager Server Launcher", 
                                font=("Arial", 16, "bold"))
        header_label.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Cấu hình Server", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Host configuration
        host_frame = ttk.Frame(config_frame)
        host_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(host_frame, text="Địa chỉ host:").pack(side=tk.LEFT)
        ttk.Radiobutton(host_frame, text="Mạng nội bộ (0.0.0.0)", 
                        variable=self.host, value="0.0.0.0").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(host_frame, text="Localhost (127.0.0.1)", 
                        variable=self.host, value="127.0.0.1").pack(side=tk.LEFT, padx=10)
        
        # Port configuration
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Cổng:").pack(side=tk.LEFT)
        port_entry = ttk.Entry(port_frame, textvariable=self.port, width=6)
        port_entry.pack(side=tk.LEFT, padx=10)
        
        # Browser option
        browser_check = ttk.Checkbutton(config_frame, text="Tự động mở trình duyệt khi server khởi động", 
                                       variable=self.open_browser)
        browser_check.pack(anchor=tk.W, pady=5)
        
        # IP information
        ip_frame = ttk.LabelFrame(main_frame, text="Thông tin mạng", padding=10)
        ip_frame.pack(fill=tk.X, pady=10)
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "Không thể xác định"
        
        ttk.Label(ip_frame, text=f"IP máy tính của bạn: {local_ip}").pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Khởi động Server", 
                                      command=self.start_server, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Dừng Server", 
                                     command=self.stop_server, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Server status
        status_frame = ttk.LabelFrame(main_frame, text="Trạng thái Server", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.status_text = tk.Text(status_frame, height=8, width=40, wrap=tk.WORD, 
                                  font=("Consolas", 10))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Mở trình duyệt", 
                  command=self.open_browser_manually).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Xem log", 
                  command=self.show_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Thoát", 
                  command=self.exit_app).pack(side=tk.RIGHT, padx=5)
    
    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def start_server(self):
        if self.is_running:
            messagebox.showinfo("Thông báo", "Server đã đang chạy!")
            return
        
        try:
            port = int(self.port.get())
            if port < 1024 or port > 65535:
                raise ValueError("Cổng không hợp lệ")
        except ValueError:
            messagebox.showerror("Lỗi", "Cổng phải là số nguyên từ 1024-65535!")
            return
        
        host = self.host.get()
        browser_arg = "" if self.open_browser.get() else "no-browser"
        
        # Xóa log cũ
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        self.update_status(f"Khởi động server trên {host}:{port}...")
        
        # Khởi động server trong thread riêng
        threading.Thread(target=self._run_server, args=(host, port, browser_arg)).start()
    
    def _run_server(self, host, port, browser_arg):
        try:
            cmd = [sys.executable, "run_network_server.py", host, str(port)]
            if browser_arg:
                cmd.append(browser_arg)
            
            # Khởi động process với pipe để có thể đọc output
            self.server_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.is_running = True
            self.root.after(0, self._update_buttons)
            
            # Đọc và hiển thị output
            for line in self.server_process.stdout:
                self.root.after(0, lambda l=line: self.update_status(l.strip()))
            
            # Khi server kết thúc
            self.server_process.wait()
            self.is_running = False
            self.server_process = None
            self.root.after(0, self._update_buttons)
            self.root.after(0, lambda: self.update_status("Server đã dừng."))
            
        except Exception as e:
            self.is_running = False
            self.root.after(0, lambda: self.update_status(f"Lỗi: {str(e)}"))
            self.root.after(0, self._update_buttons)
    
    def _update_buttons(self):
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_server(self):
        if not self.is_running or not self.server_process:
            return
        
        self.update_status("Đang dừng server...")
        
        # Dừng process (Windows)
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.server_process.pid)])
        else:
            self.server_process.terminate()
    
    def open_browser_manually(self):
        try:
            port = self.port.get()
            url = f"http://127.0.0.1:{port}"
            webbrowser.open(url)
            self.update_status(f"Đã mở trình duyệt đến {url}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở trình duyệt: {str(e)}")
    
    def show_logs(self):
        try:
            if os.path.exists("logs"):
                os.startfile("logs")
            else:
                messagebox.showinfo("Thông báo", "Thư mục logs không tồn tại!")
        except:
            messagebox.showerror("Lỗi", "Không thể mở thư mục logs!")
    
    def exit_app(self):
        if self.is_running:
            if messagebox.askyesno("Xác nhận", "Server đang chạy. Bạn có chắc muốn thoát?"):
                self.stop_server()
                time.sleep(1)  # Đợi server dừng
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerLauncher(root)
    root.mainloop()
