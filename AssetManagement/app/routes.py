from app import app, db
from app.models import Asset
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_paginate import Pagination, get_page_args
from collections import Counter
import pandas as pd
from io import BytesIO
from datetime import datetime
import os

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')
    filter_status = request.args.get('status', '')
    
    query = Asset.query
    if search_query:
        query = query.filter(
            (Asset.ma_tai_san.ilike(f'%{search_query}%')) | 
            (Asset.ten_tai_san.ilike(f'%{search_query}%'))
        )
    if filter_status:
        query = query.filter(Asset.trang_thai == filter_status)
    
    total = query.count()
    print(f"DEBUG - Total records: {total}, Page: {page}, Offset: {offset}, Per page: {per_page}")  # Debug total
    assets = query.order_by(Asset.ma_tai_san).offset(offset).limit(per_page).all()
    print(f"DEBUG - Fetched assets count: {len(assets)}, First ID: {assets[0].id if assets else 'None'}, All IDs: {[a.id for a in assets]}")  # Debug dữ liệu
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    return render_template('index.html', assets=assets, page=page, per_page=per_page, pagination=pagination, search_query=search_query, filter_status=filter_status)

@app.route('/get_asset/<id>')
def get_asset(id):
    asset = Asset.query.filter_by(ma_tai_san=id).first() or Asset.query.get_or_404(int(id))  # Thử cả ma_tai_san và id
    return jsonify({
        'id': asset.id,  # Trả về id thực sự từ database
        'ma_tai_san': asset.ma_tai_san,
        'ten_tai_san': asset.ten_tai_san,
        'ngay_vao_so': asset.ngay_vao_so.strftime('%Y-%m-%d') if asset.ngay_vao_so else '',
        'trang_thai': asset.trang_thai,
        'serial': asset.serial,
        'gia_tri': str(asset.gia_tri) if asset.gia_tri else '',
        'ngay_bao_tri': asset.ngay_bao_tri.strftime('%Y-%m-%d') if asset.ngay_bao_tri else '',
        'hang_sx': asset.hang_sx or '',
        'bo_phan': asset.bo_phan or '',  # Bổ sung trường bộ phận
        'nguoi_su_dung': asset.nguoi_su_dung or '',
        'vi_tri': asset.vi_tri or '',
        'ghi_chu': asset.ghi_chu or '',
        'image_path': asset.image_path or ''
    })

@app.route('/update_asset/<int:id>', methods=['POST'])
def update_asset(id):
    asset = Asset.query.get_or_404(id)
    asset.ma_tai_san = request.form['ma_tai_san']
    asset.ten_tai_san = request.form['ten_tai_san']
    asset.ngay_vao_so = request.form['ngay_vao_so']
    asset.trang_thai = request.form['trang_thai']
    asset.serial = request.form['serial']
    asset.gia_tri = request.form.get('gia_tri')
    asset.ngay_bao_tri = request.form.get('ngay_bao_tri')
    asset.hang_sx = request.form.get('hang_sx')
    asset.bo_phan = request.form.get('bo_phan')  # Bổ sung trường bộ phận
    asset.nguoi_su_dung = request.form.get('nguoi_su_dung')
    asset.vi_tri = request.form.get('vi_tri')
    asset.ghi_chu = request.form.get('ghi_chu')
    image = request.files.get('image')
    if image and image.filename:
        filename = f"{asset.ma_tai_san}_{image.filename}"
        image_path = os.path.join(app.static_folder, 'images', filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)
        asset.image_path = f'/static/images/{filename}'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Cập nhật thành công'})

@app.route('/add', methods=['POST'])
def add_asset():
    ma_tai_san = request.form['ma_tai_san']
    ten_tai_san = request.form['ten_tai_san']
    ngay_vao_so = request.form['ngay_vao_so']
    trang_thai = request.form['trang_thai']
    serial = request.form['serial']
    gia_tri = request.form.get('gia_tri')
    ngay_bao_tri = request.form.get('ngay_bao_tri')
    hang_sx = request.form.get('hang_sx')
    bo_phan = request.form.get('bo_phan')  # Bổ sung trường bộ phận
    nguoi_su_dung = request.form.get('nguoi_su_dung')
    vi_tri = request.form.get('vi_tri')
    ghi_chu = request.form.get('ghi_chu')
    image = request.files.get('image')
    image_path = None

    if image and image.filename:
        filename = f"{ma_tai_san}_{image.filename}"
        image_path = os.path.join(app.static_folder, 'images', filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)
        image_path = f'/static/images/{filename}'

    new_asset = Asset(ma_tai_san=ma_tai_san, ten_tai_san=ten_tai_san,
                      ngay_vao_so=ngay_vao_so, trang_thai=trang_thai,
                      serial=serial, gia_tri=gia_tri, ngay_bao_tri=ngay_bao_tri,
                      hang_sx=hang_sx, bo_phan=bo_phan, nguoi_su_dung=nguoi_su_dung, vi_tri=vi_tri, ghi_chu=ghi_chu, image_path=image_path)
    db.session.add(new_asset)
    db.session.commit()
    flash('Tài sản đã được thêm thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash('Tài sản đã được xóa thành công!', 'success')
    return redirect(url_for('index'))

# @app.route('/export')
# def export_assets():
#     assets = Asset.query.all()
#     output = "Danh sách tài sản:\n\n"
#     for asset in assets:
#         output += f"Mã: {asset.ma_tai_san}, Tên: {asset.ten_tai_san}, Ngày: {asset.ngay_vao_so}, Trạng thái: {asset.trang_thai}, Serial: {asset.serial}\n, Ghi chú: {asset.ghi_chu}\n"
#     return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/filter', methods=['GET'])
def filter_assets():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')
    filter_status = request.args.get('status', '')

    query = Asset.query
    if filter_status:
        query = query.filter_by(trang_thai=filter_status)
    if search_query:
        query = query.filter(
            (Asset.ma_tai_san.ilike(f'%{search_query}%')) | 
            (Asset.ten_tai_san.ilike(f'%{search_query}%'))
        )

    total = query.count()
    assets = query.order_by(Asset.ma_tai_san).offset(offset).limit(per_page).all()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    # Dữ liệu cho biểu đồ
    status_counts = dict(Counter(asset.trang_thai for asset in Asset.query.all()))
    return render_template('index.html', assets=assets, page=page, per_page=per_page,
                          pagination=pagination, search_query=search_query, filter_status=filter_status,
                          status_counts=status_counts)

@app.route('/chart')
def show_chart():
    status_counts = dict(Counter(asset.trang_thai for asset in Asset.query.all()))
    return render_template('chart.html', status_counts=status_counts)

@app.route('/export_excel')
def export_excel():
    select_all = request.args.get('select_all', 'false').lower() == 'true'
    selected_ids = request.args.getlist('ids[]')

    if select_all:
        # ✅ Xuất tất cả tài sản
        assets = Asset.query.all()
    elif selected_ids:
        # ✅ Xuất tài sản được chọn
        assets = Asset.query.filter(Asset.id.in_(selected_ids)).all()
    else:
        return "Không có tài sản nào được chọn", 400

    df = pd.DataFrame([
        (a.ma_tai_san, a.ten_tai_san, a.ngay_vao_so, a.trang_thai, a.serial, a.gia_tri,
         a.ngay_bao_tri, a.hang_sx, a.nguoi_su_dung, a.bo_phan, a.vi_tri, a.ghi_chu, a.image_path)
        for a in assets
    ], columns=['Mã tài sản', 'Tên tài sản', 'Ngày vào sổ', 'Trạng thái', 'Serial', 'Giá trị',
                'Ngày bảo trì', 'Hãng sản xuất', 'Người sử dụng', 'Bộ phận', 'Vị trí', 'Ghi chú', 'Đường dẫn ảnh'])

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name='assets.xlsx', as_attachment=True)


@app.route('/asset_detail/<int:id>')
def asset_detail(id):
    asset = Asset.query.get_or_404(id)
    return render_template('asset_detail.html', asset=asset)

@app.route('/search_asset')
def search_asset():
    search_query = request.args.get('search', '')
    if search_query:
        asset = Asset.query.filter(
            (Asset.ma_tai_san.ilike(f'%{search_query}%')) | 
            (Asset.ten_tai_san.ilike(f'%{search_query}%'))
        ).first()
        if asset:
            return jsonify({
                'id': asset.id,
                'ma_tai_san': asset.ma_tai_san,
                'ten_tai_san': asset.ten_tai_san,
                'ngay_vao_so': asset.ngay_vao_so.strftime('%Y-%m-%d') if asset.ngay_vao_so else '',
                'trang_thai': asset.trang_thai,
                'serial': asset.serial,
                'gia_tri': str(asset.gia_tri) if asset.gia_tri else '',
                'ngay_bao_tri': asset.ngay_bao_tri.strftime('%Y-%m-%d') if asset.ngay_bao_tri else '',
                'hang_sx': asset.hang_sx or '',
                'nguoi_su_dung': asset.nguoi_su_dung or '',
                'bo_phan': asset.bo_phan or '',
                'vi_tri': asset.vi_tri or '',
                'ghi_chu': asset.ghi_chu or '',
                'image_path': asset.image_path or ''
            })
    return jsonify({})

from flask import request
from datetime import datetime