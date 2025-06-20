# 数据库配置信息
HOSTNAME = '127.0.0.1'
PORT = 3306
DATABASE = 'zhiliaoa'
USERNAME = 'root'
PASSWORD = '3306'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

# 邮箱配置
# MAIL_USERNAME 与 DEFAULT_MAIL_SENDER必须一样
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_DEBUG = True
MAIL_USERNAME = "758370266@qq.com"
MAIL_PASSWORD = "otoorxqclgmdbbgb"
MAIL_DEFAULT_SENDER = "758370266@qq.com"

# redis配置
REDIS_URL = "redis://:@localhost:6379/0"
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
REDIS_DEFAULT_EXPIRATION = 60 * 60 * 24 * 7

# （低版本）解决中文乱码
JSON_AS_ASCII = False
JSONIFY_MIMETYPE = "application/json;charset=utf-8"