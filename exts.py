# 为了解决循环引用的问题
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()
redis = FlaskRedis()