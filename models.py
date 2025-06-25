from exts import db
from datetime import datetime

CHARSET_CONFIG = {
    'mysql_charset': 'utf8mb4',
    'mysql_collate': 'utf8mb4_unicode_ci'
}

class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = CHARSET_CONFIG  # 设置字符集
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(128), unique=True, nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)

class EmailCaptchaModel(db.Model):
    __tablename__ = 'email_captcha'
    __table_args__ = CHARSET_CONFIG  # 设置字符集
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), nullable=False)
    captcha = db.Column(db.String(128), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

class IntelligenceModel(db.Model):
    __tablename__ = 'intelligence'
    __table_args__ = CHARSET_CONFIG  # 设置字符集
    id = db.Column(db.String(128), primary_key=True)
    content = db.Column(db.Text)
    insert_time = db.Column(db.DateTime)  
    label_name = db.Column(db.String(128))  
    user_name = db.Column(db.String(128))  
    area = db.Column(db.String(128))  
    threaten_level = db.Column(db.String(128))
    status = db.Column(db.String(128))
    source = db.Column(db.String(128))
    suspicious_organization = db.Column(db.String(128))
    suspicious_user = db.Column(db.String(128))


