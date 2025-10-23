# Định nghĩa các model (bảng Assets, Users)
from app import db
from sqlalchemy import Unicode

class Asset(db.Model):
    __tablename__ = 'Assets'
    id = db.Column(db.Integer, primary_key=True)
    ma_tai_san = db.Column(db.String(20), nullable=False, unique=True)
    ten_tai_san = db.Column(Unicode(100))
    ngay_vao_so = db.Column(db.Date, nullable=False)
    trang_thai = db.Column(Unicode(50))
    serial = db.Column(db.String(50), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    gia_tri = db.Column(db.Float, nullable=True)
    ngay_bao_tri = db.Column(db.Date)
    hang_sx = db.Column(Unicode(100))
    nguoi_su_dung = db.Column(Unicode(100))
    bo_phan = db.Column(Unicode(100))
    vi_tri = db.Column(Unicode(100))
    ghi_chu = db.Column(db.Text)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)