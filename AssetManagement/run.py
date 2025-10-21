# File chạy ứng dụng Flask
from app import app

if __name__ == '__main__':
    with app.app_context():
        # Tạo các bảng trong database nếu chưa có
        from app.models import Asset, User
        app.config['SQLALCHEMY_ECHO'] = True  # Hiển thị query SQL (dùng để debug)
        app.run(host='0.0.0.0', port=5000, debug=True)