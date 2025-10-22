CREATE DATABASE quan_ly_tai_san;

USE quan_ly_tai_san;
GO

CREATE TABLE Assets (
    id INT IDENTITY(1,1) PRIMARY KEY,
    ma_tai_san VARCHAR(20),
    ten_tai_san VARCHAR(100),
    ngay_vao_so DATE,
    trang_thai VARCHAR(20),
    barcode VARCHAR(50)
);

CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL
);



--Đổi tên trường "nhom_tai_san" thành "vi_tri"-------------------------------------------
EXEC sp_rename '[quan_ly_tai_san].[dbo].[Assets].nhom_tai_san', 'vi_tri', 'COLUMN';
-----------------------------------------------------------------------------------------

INSERT INTO Users (username, role) VALUES ('admin', 'admin1');
INSERT INTO Users (username, role) VALUES ('user1', 'user1');
SELECT * FROM Users;
SELECT * FROM Assets;