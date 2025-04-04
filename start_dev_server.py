"""
Script khởi chạy môi trường phát triển cho Python Manager
Sử dụng để chạy ứng dụng trong môi trường venv
"""
import os
import sys
import subprocess

def main():
    print("Python Manager - Development Server")
    print("-----------------------------------")
    
    # Kiểm tra môi trường venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("\nWARNING: Not running in a virtual environment!")
        print("It's recommended to activate your venv first with:")
        print("  venv\\Scripts\\activate  (on Windows)")
        print("  source venv/bin/activate  (on Linux/Mac)")
        
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    else:
        print(f"Using Python from: {sys.executable}")
        print(f"Virtual environment: {sys.prefix}")
    
    # Cài đặt dependencies
    print("\nChecking dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_windows.txt"])
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Please install them manually.")
        return
    
    # Thiết lập biến môi trường
    os.environ['FLASK_APP'] = 'app'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Import và chạy ứng dụng
    print("\nStarting Flask development server...")
    
    # Sử dụng cách 1: Import trực tiếp app và chạy
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
    except Exception as e:
        print(f"Error starting Flask server directly: {e}")
        
        # Sử dụng cách 2: Chạy flask qua subprocess
        print("\nTrying alternative method...")
        try:
            subprocess.check_call([sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"])
        except Exception as e:
            print(f"Error starting Flask server via CLI: {e}")
            return

if __name__ == "__main__":
    main()
