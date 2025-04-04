# Xử lý sự cố kết nối mạng cho Python Manager

Nếu bạn gặp vấn đề khi cố gắng truy cập Flask server từ các thiết bị khác trong mạng LAN, hãy thử các giải pháp sau:

## 1. Kiểm tra tường lửa

### Windows Firewall
1. Mở Windows Defender Firewall bằng cách tìm kiếm "firewall" trong menu Start
2. Nhấp vào "Allow an app or feature through Windows Defender Firewall"
3. Nhấp vào "Change settings"
4. Nhấp vào "Allow another app..." 
5. Tìm đến file python.exe hoặc thêm cổng 5000 vào danh sách cho phép
6. Đảm bảo rằng cả "Private" và "Public" đều được chọn

Hoặc, để nhanh chóng kiểm tra, bạn có thể tạm thời tắt Windows Firewall:
1. Mở Windows Defender Firewall
2. Nhấp vào "Turn Windows Defender Firewall on or off"
3. Chọn "Turn off Windows Defender Firewall" cho cả mạng Private và Public
4. Nhấp vào "OK"

### Phần mềm bảo mật khác
Nếu bạn đang sử dụng phần mềm antivirus hoặc bảo mật khác, hãy kiểm tra cài đặt tường lửa của nó.

## 2. Kiểm tra cấu hình Router

Đảm bảo rằng Router không chặn kết nối nội bộ giữa các thiết bị trong mạng LAN.

## 3. Sử dụng script khởi động mạng

Sử dụng file `run_network_server.py` để khởi động server:

```bash
python run_network_server.py
```

Hoặc chỉ định địa chỉ IP và cổng:

```bash
python run_network_server.py 0.0.0.0 8080
```

## 4. Thử một cổng khác

Nếu cổng 5000 bị chặn hoặc đang được sử dụng, hãy thử một cổng khác như 8080:

```bash
python run_network_server.py 0.0.0.0 8080
```

## 5. Kiểm tra kết nối bằng Telnet

Để kiểm tra xem cổng có mở và có thể truy cập từ thiết bị khác:

Trên Windows, mở Command Prompt và nhập:
