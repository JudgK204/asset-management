USE quan_ly_tai_san;
GO

select * from [quan_ly_tai_san].[dbo].[Phieu_Nhap] GO
select * from [quan_ly_tai_san].[dbo].[Phieu_Nhap_Chi_Tiet] GO
select * from [quan_ly_tai_san].[dbo].[Vat_Tu_Tong]

DELETE FROM [quan_ly_tai_san].[dbo].[Phieu_Nhap_Chi_Tiet]; 
DELETE FROM [quan_ly_tai_san].[dbo].[Vat_Tu_Tong]; 
DELETE FROM [quan_ly_tai_san].[dbo].[Phieu_Nhap];
DELETE FROM [quan_ly_tai_san].[dbo].[TransactionHistory]

DBCC CHECKIDENT ('[quan_ly_tai_san].[dbo].[Phieu_Nhap]', RESEED, 0); 
DBCC CHECKIDENT ('[quan_ly_tai_san].[dbo].[Phieu_Nhap_Chi_Tiet]', RESEED, 0); 
DBCC CHECKIDENT ('[quan_ly_tai_san].[dbo].[Vat_Tu_Tong]', RESEED, 0); 
DBCC CHECKIDENT ('[quan_ly_tai_san].[dbo].[TransactionHistory]', RESEED, 0); 

-- ... tiếp tục cho đến khi xóa hết các bảng con

-- Bảng vật tư tổng
CREATE TABLE Vat_Tu_Tong (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    ma_vat_tu NVARCHAR(20) UNIQUE NOT NULL,
    ten_vat_tu NVARCHAR(255) NOT NULL,
    loai_vat_tu NVARCHAR(50) NOT NULL, -- Văn phòng / Sản xuất / Sửa chữa
    don_vi_tinh NVARCHAR(50) NULL,
    so_luong_ton INT DEFAULT 0,
    ly_do NVARCHAR(255) NULL,
    ngay_tao DATETIME DEFAULT GETDATE(),
    trang_thai NVARCHAR(50) DEFAULT N'Con hang'
);
GO

-- Bảng phiếu nhập
CREATE TABLE Phieu_Nhap (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) UNIQUE NOT NULL,
    ngay_nhap DATETIME DEFAULT GETDATE(),
    nguoi_giao NVARCHAR(100),
    phong_ban_nguoi_giao NVARCHAR(100),
    nguoi_nhap_kho NVARCHAR(100),
    phong_ban_nguoi_nhap_kho NVARCHAR(100),
    ly_do_nhap NVARCHAR(255),
    ghi_chu NVARCHAR(255) NULL
);
GO

-- Bảng chi tiết phiếu nhập
CREATE TABLE Phieu_Nhap_Chi_Tiet (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) NOT NULL,
    ma_vat_tu NVARCHAR(20) NOT NULL,
    ten_vat_tu NVARCHAR(255) NOT NULL,
    don_vi_tinh NVARCHAR(50),
    so_luong INT NOT NULL,
    ly_do NVARCHAR(255) NULL,
    CONSTRAINT FK_Nhap_Phieu FOREIGN KEY (so_phieu) REFERENCES Phieu_Nhap(so_phieu),
    CONSTRAINT FK_Nhap_VatTu FOREIGN KEY (ma_vat_tu) REFERENCES Vat_Tu_Tong(ma_vat_tu)
);
GO

-- Bảng phiếu xuất
CREATE TABLE Phieu_Xuat (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) UNIQUE NOT NULL,
    ngay_xuat DATETIME DEFAULT GETDATE(),
    nguoi_xuat NVARCHAR(100),
    phong_ban_nguoi_xuat NVARCHAR(100),
    nguoi_nhan NVARCHAR(100),
    phong_ban_nguoi_nhan NVARCHAR(100),
    ly_do_xuat NVARCHAR(255),
    ghi_chu NVARCHAR(255) NULL
);
GO

-- Bảng chi tiết phiếu xuất
CREATE TABLE Phieu_Xuat_Chi_Tiet (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) NOT NULL,
    ma_vat_tu NVARCHAR(20) NOT NULL,
    ten_vat_tu NVARCHAR(255),
    don_vi_tinh NVARCHAR(50),
    so_luong INT NOT NULL,
    ly_do NVARCHAR(255) NULL,
    CONSTRAINT FK_Xuat_Phieu FOREIGN KEY (so_phieu) REFERENCES Phieu_Xuat(so_phieu),
    CONSTRAINT FK_Xuat_VatTu FOREIGN KEY (ma_vat_tu) REFERENCES Vat_Tu_Tong(ma_vat_tu)
);
GO

-- Bảng phiếu hủy
CREATE TABLE Phieu_Huy (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) UNIQUE NOT NULL,
    ngay_huy DATETIME DEFAULT GETDATE(),
    nguoi_huy NVARCHAR(100),
    phong_ban_nguoi_huy NVARCHAR(100),
    ly_do_huy NVARCHAR(255),
    ghi_chu NVARCHAR(255) NULL
);
GO

-- Bảng chi tiết phiếu hủy
CREATE TABLE Phieu_Huy_Chi_Tiet (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20) NOT NULL,
    ma_vat_tu NVARCHAR(20) NOT NULL,
    ten_vat_tu NVARCHAR(255),
    don_vi_tinh NVARCHAR(50),
    so_luong INT NOT NULL,
    ly_do NVARCHAR(255) NULL,
    CONSTRAINT FK_Huy_Phieu FOREIGN KEY (so_phieu) REFERENCES Phieu_Huy(so_phieu),
    CONSTRAINT FK_Huy_VatTu FOREIGN KEY (ma_vat_tu) REFERENCES Vat_Tu_Tong(ma_vat_tu)
);
GO

-- Trigger nhập kho -> tăng số lượng tồn
CREATE TRIGGER trg_AfterInsert_Nhap
ON Phieu_Nhap_Chi_Tiet
AFTER INSERT
AS
BEGIN
    UPDATE Vat_Tu_Tong
    SET so_luong_ton = so_luong_ton + i.so_luong
    FROM Vat_Tu_Tong vt
    JOIN inserted i ON vt.ma_vat_tu = i.ma_vat_tu;
END;
GO
-- Bảng lịch sử
CREATE TABLE TransactionHistory (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    so_phieu NVARCHAR(20),           -- voucher number
    ma_vat_tu NVARCHAR(20),          -- asset code
    ten_vat_tu NVARCHAR(100),        -- asset name
    loai_giao_dich NVARCHAR(20),     -- transaction type: Nhập / Xuất / Hủy
    so_luong INT,                    -- quantity
    nguoi_thuc_hien NVARCHAR(100),   -- executor
    phong_ban NVARCHAR(100),         -- department
    ngay_giao_dich DATETIME DEFAULT GETDATE(), -- transaction date
    ghi_chu NVARCHAR(255)            -- note
);
GO



-- Trigger xuất kho -> giảm số lượng tồn
CREATE TRIGGER trg_AfterInsert_Xuat
ON Phieu_Xuat_Chi_Tiet
AFTER INSERT
AS
BEGIN
    UPDATE Vat_Tu_Tong
    SET so_luong_ton = so_luong_ton - i.so_luong
    FROM Vat_Tu_Tong vt
    JOIN inserted i ON vt.ma_vat_tu = i.ma_vat_tu;
END;
GO

-- Trigger hủy vật tư -> giảm tồn và cập nhật trạng thái
CREATE TRIGGER trg_AfterInsert_Huy
ON Phieu_Huy_Chi_Tiet
AFTER INSERT
AS
BEGIN
    UPDATE Vat_Tu_Tong
    SET so_luong_ton = so_luong_ton - i.so_luong,
        trang_thai = CASE 
            WHEN so_luong_ton - i.so_luong <= 0 THEN N'Da huy'
            ELSE trang_thai
        END
    FROM Vat_Tu_Tong vt
    JOIN inserted i ON vt.ma_vat_tu = i.ma_vat_tu;
END;
GO
