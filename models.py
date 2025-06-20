from exts import db
from datetime import datetime

class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(128), unique=True, nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)

class EmailCaptchaModel(db.Model):
    __tablename__ = 'email_captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), nullable=False)
    captcha = db.Column(db.String(128), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)