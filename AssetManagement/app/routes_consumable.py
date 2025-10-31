from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models import db, VatTuTong, PhieuNhap, PhieuNhapChiTiet, PhieuXuat, PhieuXuatChiTiet, PhieuHuy, PhieuHuyChiTiet, TransactionHistory
from datetime import datetime, date
from sqlalchemy.sql import text

consumable_bp = Blueprint('consumable', __name__)

# --- Helper: Sinh mã vật tư tự động ---
def generate_ma_vattu(loai_vat_tu):
    prefix = {"Văn phòng": "VP", "Sản xuất": "SX", "Sửa chữa": "SC"}.get(loai_vat_tu, "XX")
    last_item = VatTuTong.query.filter(VatTuTong.ma_vat_tu.like(f"{prefix}%")).order_by(VatTuTong.id.desc()).first()
    
    print(f"[DEBUG] generate_ma_vattu: loai={loai_vat_tu}, last={last_item.ma_vat_tu if last_item else 'None'}")
    
    next_num = 1
    if last_item and last_item.ma_vat_tu:
        try:
            num_part = last_item.ma_vat_tu.replace(prefix, "")
            next_num = int(num_part) + 1
        except ValueError:
            pass
    return f"{prefix}{next_num:07d}"

# --- Helper: Sinh số phiếu tự động ---
def generate_so_phieu():
    today = datetime.now().strftime("%d%m%Y")
    last = PhieuNhap.query.filter(PhieuNhap.so_phieu.like(f"{today}%")).order_by(PhieuNhap.id.desc()).first()
    print("Last phiếu:", last.so_phieu if last else "None")  # ← Thêm debug
    next_num = 1
    if last and last.so_phieu:
        num_part = last.so_phieu.replace(today, "")
        next_num = int(num_part) + 1 if num_part.isdigit() else 1
    return f"{today}{next_num:04d}"

# === Trang chính: Quản lý vật tư tổng ===
@consumable_bp.route("/consumable")
def consumable_index():
    # LẤY TẤT CẢ VẬT TƯ
    vattu_list = VatTuTong.query.order_by(VatTuTong.ma_vat_tu).all()

    # DEBUG: In ra console
    print(f"[DEBUG] Số vật tư: {len(vattu_list)}")
    for vt in vattu_list:
        print(f"  → {vt.ma_vat_tu} | {vt.ten_vat_tu} | SL: {vt.so_luong_ton} | TT: {vt.trang_thai}")

    return render_template(
        "consumable/index_consumable.html",  # ← TÊN FILE ĐÚNG
        vattu_list=vattu_list
    )

def prefix_from_loai(loai):
    return {"Văn phòng": "VP", "Sản xuất": "SX", "Sửa chữa": "SC"}.get(loai, "")

# === Nhập kho ===
@consumable_bp.route("/consumable/nhap", methods=["GET", "POST"])
def consumable_nhap():
    if request.method == "POST" and 'preview_data' in request.form:
        import json
        data = json.loads(request.form['preview_data'])
        so_phieu = data.get("so_phieu") or generate_so_phieu()

        # XỬ LÝ MÃ VẬT TƯ
        processed_items = []
        last_ma_by_type = {}

        for item in data.get("items", []):
            loai = item.get("loai_vat_tu")
            if not loai: continue

            prefix = prefix_from_loai(loai)
            current_ma = item.get("ma_vat_tu", "")

            if current_ma and current_ma.startswith(prefix):
                new_ma = current_ma
            else:
                last_ma = last_ma_by_type.get(loai)
                if last_ma:
                    num = int(last_ma.replace(prefix, "")) + 1
                else:
                    last_db = VatTuTong.query.filter(VatTuTong.ma_vat_tu.like(f"{prefix}%"))\
                                            .order_by(VatTuTong.id.desc()).first()
                    num = int(last_db.ma_vat_tu.replace(prefix, "")) + 1 if last_db else 1
                new_ma = f"{prefix}{num:07d}"
                last_ma_by_type[loai] = new_ma

            processed_items.append({**item, "ma_vat_tu": new_ma})

        # LƯU SESSION
        session['temp_data'] = {
            'so_phieu': so_phieu,
            'ngay_nhap': data.get("ngay_nhap"),
            'nguoi_nhap': data.get("nguoi_nhap_kho"),
            'phong_ban_nhap': data.get("phong_ban_nguoi_nhap_kho"),
            'ghi_chu': data.get("ghi_chu"),
            'nguoi_giao': data.get("nguoi_giao"),
            'phong_ban_giao': data.get("phong_ban_nguoi_giao"),
            'items': processed_items
        }

        return render_template('consumable/report_nhap.html', data=session['temp_data'])

    # GET: form nhập
    if 'temp_data' not in session:
        session['temp_data'] = {
            'so_phieu': generate_so_phieu(),
            'ngay_nhap': datetime.now().strftime('%Y-%m-%d'),
            'nguoi_nhap': '', 'phong_ban_nhap': '', 'ghi_chu': '',
            'nguoi_giao': '', 'phong_ban_giao': '', 'items': []
        }
    return render_template("consumable/nhap.html", data=session['temp_data'])

# === Xác nhận và lưu phiếu nhập ===
@consumable_bp.route("/consumable/nhap/confirm", methods=["POST"])
def consumable_nhap_confirm():
    if request.form.get('confirmed') != '1':
        return "<div class='text-red-500'>Lỗi: Yêu cầu không hợp lệ!</div>"

    temp_data = session.get('temp_data')
    if not temp_data:
        return "<div class='text-red-500'>Lỗi: Không có dữ liệu!</div>"

    so_phieu = temp_data['so_phieu']
    if PhieuNhap.query.filter_by(so_phieu=so_phieu).first():
        session.pop('temp_data', None)
        return f"<div class='text-yellow-500'>Phiếu {so_phieu} đã tồn tại!</div>"

    try:
        # === CHUYỂN NGÀY ===
        ngay_nhap_str = temp_data['ngay_nhap']
        ngay_nhap_date = datetime.strptime(ngay_nhap_str, "%Y-%m-%d").date()
        ngay_nhap = datetime.combine(ngay_nhap_date, datetime.min.time())

        # === LƯU PHIẾU ===
        phieu = PhieuNhap(
            so_phieu=so_phieu, ngay_nhap=ngay_nhap,
            nguoi_giao=temp_data['nguoi_giao'], phong_ban_nguoi_giao=temp_data['phong_ban_giao'],
            nguoi_nhap_kho=temp_data['nguoi_nhap'], phong_ban_nguoi_nhap_kho=temp_data['phong_ban_nhap'],
            ghi_chu=temp_data['ghi_chu']
        )
        db.session.add(phieu)
        db.session.commit()  # ← COMMIT ĐỂ CÓ so_phieu

        # === THÊM VẬT TƯ ===
        for item in temp_data['items']:
            ma_vt = item['ma_vat_tu']
            vt = VatTuTong.query.filter_by(ma_vat_tu=ma_vt).first()
            if not vt:
                vt = VatTuTong(
                    ma_vat_tu=ma_vt, ten_vat_tu=item['ten_vat_tu'],
                    loai_vat_tu=item['loai_vat_tu'], don_vi_tinh=item['don_vi_tinh'],
                    so_luong_ton=0
                )
                db.session.add(vt)
        db.session.commit()  # ← COMMIT ĐỂ VẬT TƯ TỒN TẠI

        # === LƯU CHI TIẾT + LỊCH SỬ ===
        for item in temp_data['items']:
            ma_vt = item['ma_vat_tu']
            sl = int(item['so_luong'])

            vt = VatTuTong.query.filter_by(ma_vat_tu=ma_vt).first()
            vt.so_luong_ton += sl
            vt.trang_thai = 'Con hang' if vt.so_luong_ton > 0 else 'Het hang'

            # LƯU CHI TIẾT (không cần id)
            ct = PhieuNhapChiTiet(
                so_phieu=so_phieu, ma_vat_tu=ma_vt,
                ten_vat_tu=item['ten_vat_tu'], don_vi_tinh=item['don_vi_tinh'],
                so_luong=sl, ly_do=item.get('ly_do', '')
            )
            db.session.add(ct)

            db.session.add(TransactionHistory(
                ngay_giao_dich=ngay_nhap, so_phieu=so_phieu,
                loai_giao_dich='Nhập kho', ma_vat_tu=ma_vt,
                ten_vat_tu=item['ten_vat_tu'], so_luong=sl,
                nguoi_thuc_hien=temp_data['nguoi_nhap'], phong_ban=temp_data['phong_ban_nhap'],
                ghi_chu=temp_data['ghi_chu']
            ))

        db.session.commit()  # ← COMMIT CUỐI
        session.pop('temp_data', None)

        return f"""
        <div class='text-green-500 font-bold text-lg'>Nhập kho thành công – phiếu {so_phieu}</div>
        <script>
            setTimeout(() => {{ window.location = '{url_for("consumable.consumable_nhap")}'; }}, 1500);
        </script>
        """

    except Exception as e:
        db.session.rollback()
        return f"<div class='text-red-500'>Lỗi: {str(e)}</div>"
    
# === Xuất kho ===
@consumable_bp.route("/consumable/xuat", methods=["GET", "POST"])
def consumable_xuat():
    items = VatTuTong.query.filter(VatTuTong.trang_thai != 'Da huy').all()
    if request.method == "POST":
        ma_vat_tu = request.form.get("ma_vat_tu")
        so_luong = int(request.form.get("so_luong", 0))
        nguoi_xuat = request.form.get("nguoi_xuat")
        phong_ban_nguoi_xuat = request.form.get("phong_ban_nguoi_xuat")
        nguoi_nhan = request.form.get("nguoi_nhan")
        phong_ban_nguoi_nhan = request.form.get("phong_ban_nguoi_nhan")
        ly_do_xuat = request.form.get("ly_do_xuat")
        ngay_xuat = request.form.get("ngay_xuat") or datetime.now().date()
        ghi_chu = request.form.get("ghi_chu")

        vat_tu = VatTuTong.query.filter_by(ma_vat_tu=ma_vat_tu).first()
        if not vat_tu or vat_tu.so_luong_ton < so_luong:
            flash("Không đủ số lượng để xuất!", "error")
            return redirect(url_for("consumable.consumable_xuat"))

        # Ghi phiếu xuất
        so_phieu = generate_so_phieu()
        phieu = PhieuXuat(
            so_phieu=so_phieu,
            ngay_xuat=ngay_xuat,
            nguoi_xuat=nguoi_xuat,
            phong_ban_nguoi_xuat=phong_ban_nguoi_xuat,
            nguoi_nhan=nguoi_nhan,
            phong_ban_nguoi_nhan=phong_ban_nguoi_nhan,
            ly_do_xuat=ly_do_xuat,
            ghi_chu=ghi_chu
        )
        db.session.add(phieu)
        db.session.flush()

        chi_tiet = PhieuXuatChiTiet(
            so_phieu=so_phieu,
            ma_vat_tu=ma_vat_tu,
            ten_vat_tu=vat_tu.ten_vat_tu,
            don_vi_tinh=vat_tu.don_vi_tinh,
            so_luong=so_luong,
            ly_do=ly_do_xuat
        )
        db.session.add(chi_tiet)
        db.session.commit()
        flash("Xuất kho thành công!", "success")
        return redirect(url_for("consumable.consumable_index"))

    return render_template("consumable/xuat.html", items=items)

# === Hủy vật tư ===
@consumable_bp.route("/consumable/huy", methods=["GET", "POST"])
def consumable_huy():
    items = VatTuTong.query.filter(VatTuTong.trang_thai != 'Da huy').all()
    if request.method == "POST":
        ma_vat_tu = request.form.get("ma_vat_tu")
        so_luong = int(request.form.get("so_luong", 0))
        nguoi_huy = request.form.get("nguoi_huy")
        phong_ban_nguoi_huy = request.form.get("phong_ban_nguoi_huy")
        ly_do_huy = request.form.get("ly_do_huy")
        ngay_huy = request.form.get("ngay_huy") or datetime.now().date()
        ghi_chu = request.form.get("ghi_chu")

        vat_tu = VatTuTong.query.filter_by(ma_vat_tu=ma_vat_tu).first()
        if not vat_tu or vat_tu.so_luong_ton < so_luong:
            flash("Không đủ số lượng để hủy!", "error")
            return redirect(url_for("consumable.consumable_huy"))

        so_phieu = generate_so_phieu()
        phieu = PhieuHuy(
            so_phieu=so_phieu,
            ngay_huy=ngay_huy,
            nguoi_huy=nguoi_huy,
            phong_ban_nguoi_huy=phong_ban_nguoi_huy,
            ly_do_huy=ly_do_huy,
            ghi_chu=ghi_chu
        )
        db.session.add(phieu)
        db.session.flush()

        chi_tiet = PhieuHuyChiTiet(
            so_phieu=so_phieu,
            ma_vat_tu=ma_vat_tu,
            ten_vat_tu=vat_tu.ten_vat_tu,
            don_vi_tinh=vat_tu.don_vi_tinh,
            so_luong=so_luong,
            ly_do=ly_do_huy
        )
        db.session.add(chi_tiet)
        db.session.commit()
        flash("Hủy vật tư thành công!", "success")
        return redirect(url_for("consumable.consumable_index"))

    return render_template("consumable/huy.html", items=items)

@consumable_bp.route('/history')
def transaction_history():
    search = request.args.get('search', '')
    type_filter = request.args.get('type', '')

    query = TransactionHistory.query.order_by(TransactionHistory.ngay_giao_dich.desc())

    if search:
        query = query.filter(TransactionHistory.ma_vat_tu.ilike(f"%{search}%"))
    if type_filter:
        query = query.filter(TransactionHistory.loai_giao_dich == type_filter)

    history = query.all()
    return render_template('consumable/history.html', history=history)
