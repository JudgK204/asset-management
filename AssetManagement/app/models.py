# Định nghĩa các model (bảng Assets, Users)
from app import db
from sqlalchemy import Unicode
from datetime import datetime

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
# ==========================
#   MODULE: TÀI SẢN TIÊU HAO
# ==========================
class VatTuTong(db.Model):
    __tablename__ = 'Vat_Tu_Tong' 
    id = db.Column(db.Integer, primary_key=True)
    ma_vat_tu = db.Column(db.String(20), unique=True, nullable=False)
    ten_vat_tu = db.Column(db.String(255), nullable=False)
    loai_vat_tu = db.Column(db.String(50), nullable=False)
    don_vi_tinh = db.Column(db.String(50))
    so_luong_ton = db.Column(db.Integer, default=0)
    ly_do = db.Column(db.String(255))
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    trang_thai = db.Column(db.String(50), default='Con hang')

    # ← DÙNG backref → KHÔNG CẦN ForeignKey ở đây
    phieu_nhap_ct = db.relationship('PhieuNhapChiTiet', backref='vattu', lazy='dynamic')
    phieu_xuat_ct = db.relationship('PhieuXuatChiTiet', backref='vattu', lazy='dynamic')
    phieu_huy_ct = db.relationship('PhieuHuyChiTiet', backref='vattu', lazy='dynamic')

# ====================
#   PHIẾU NHẬP
# ====================
class PhieuNhap(db.Model):
    __tablename__ = 'Phieu_Nhap'
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), unique=True, nullable=False)
    ngay_nhap = db.Column(db.DateTime, default=datetime.utcnow)
    nguoi_giao = db.Column(db.String(100))
    phong_ban_nguoi_giao = db.Column(db.String(100))
    nguoi_nhap_kho = db.Column(db.String(100))
    phong_ban_nguoi_nhap_kho = db.Column(db.String(100))
    ly_do_nhap = db.Column(db.String(255))
    ghi_chu = db.Column(db.String(255))

    chi_tiet = db.relationship('PhieuNhapChiTiet', backref='phieu', lazy=True)

class PhieuNhapChiTiet(db.Model):
    __tablename__ = 'Phieu_Nhap_Chi_Tiet'
    __table_args__ = {'implicit_returning': False}  # ← FIX CHÍNH
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), db.ForeignKey('Phieu_Nhap.so_phieu'), nullable=False)
    ma_vat_tu = db.Column(db.String(20), db.ForeignKey('Vat_Tu_Tong.ma_vat_tu'), nullable=False)  # Sửa ForeignKey để khớp tên bảng có dấu gạch dưới
    ten_vat_tu = db.Column(db.String(255))
    don_vi_tinh = db.Column(db.String(50))
    so_luong = db.Column(db.Integer, nullable=False)
    ly_do = db.Column(db.String(255))

# ====================
#   PHIẾU XUẤT
# ====================
class PhieuXuat(db.Model):
    __tablename__ = 'Phieu_Xuat'
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), unique=True, nullable=False)
    ngay_xuat = db.Column(db.DateTime, default=datetime.utcnow)
    nguoi_xuat = db.Column(db.String(100))
    phong_ban_nguoi_xuat = db.Column(db.String(100))
    nguoi_nhan = db.Column(db.String(100))
    phong_ban_nguoi_nhan = db.Column(db.String(100))
    ly_do_xuat = db.Column(db.String(255))
    ghi_chu = db.Column(db.String(255))

    chi_tiet = db.relationship('PhieuXuatChiTiet', backref='phieu', lazy=True)

class PhieuXuatChiTiet(db.Model):
    __tablename__ = 'Phieu_Xuat_Chi_Tiet'
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), db.ForeignKey('Phieu_Xuat.so_phieu'), nullable=False)
    
    # ← SỬA: 'Vat_Tu_Tong.ma_vat_tu' (có gạch dưới)
    ma_vat_tu = db.Column(db.String(20), db.ForeignKey('Vat_Tu_Tong.ma_vat_tu'), nullable=False)
    
    ten_vat_tu = db.Column(db.String(255))
    don_vi_tinh = db.Column(db.String(50))
    so_luong = db.Column(db.Integer, nullable=False)
    ly_do = db.Column(db.String(255))

# ====================
#   PHIẾU HỦY
# ====================
class PhieuHuy(db.Model):
    __tablename__ = 'Phieu_Huy'
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), unique=True, nullable=False)
    ngay_huy = db.Column(db.DateTime, default=datetime.utcnow)
    nguoi_huy = db.Column(db.String(100))
    phong_ban_nguoi_huy = db.Column(db.String(100))
    ly_do_huy = db.Column(db.String(255))
    ghi_chu = db.Column(db.String(255))

    chi_tiet = db.relationship('PhieuHuyChiTiet', backref='phieu', lazy=True)

class PhieuHuyChiTiet(db.Model):
    __tablename__ = 'Phieu_Huy_Chi_Tiet'
    id = db.Column(db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20), db.ForeignKey('Phieu_Huy.so_phieu'), nullable=False)
    ma_vat_tu = db.Column(db.String(20), db.ForeignKey('Vat_Tu_Tong.ma_vat_tu'), nullable=False)  # Sửa ForeignKey để khớp tên bảng có dấu gạch dưới
    ten_vat_tu = db.Column(db.String(255))
    don_vi_tinh = db.Column(db.String(50))
    so_luong = db.Column(db.Integer, nullable=False)
    ly_do = db.Column(db.String(255))

# ====================
#   LỊCH SỬ
# ====================

class TransactionHistory(db.Model):
    __tablename__ = "TransactionHistory"

    id = db.Column("ID", db.Integer, primary_key=True)
    so_phieu = db.Column(db.String(20))
    ma_vat_tu = db.Column(db.String(20))
    ten_vat_tu = db.Column(db.String(100))
    loai_giao_dich = db.Column(db.String(20))
    so_luong = db.Column(db.Integer)
    nguoi_thuc_hien = db.Column(db.String(100))
    phong_ban = db.Column(db.String(100))
    ngay_giao_dich = db.Column(db.DateTime)
    ghi_chu = db.Column(db.String(255))