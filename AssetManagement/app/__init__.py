# Khởi tạo ứng dụng Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pyodbc

app = Flask(__name__)#, template_folder='app/templates', static_folder='static', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://sa:12@localhost\\ADMINISTRATOR/quan_ly_tai_san?'
    'driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no&charset=utf8&TrustServerCertificate=yes'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Để debug
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

print("Importing routes...")
from app import routes
print("Routes imported successfully.")