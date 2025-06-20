from flask import Flask
import config
from exts import db
from exts import mail
from exts import redis
from models import UserModel
from blueprints.qa import bp as qa_bp
from blueprints.auth import bp as auth_bp
from flask_migrate import Migrate


app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)
redis.init_app(app)

migrate = Migrate(app, db)
# 迁移三部曲
# flask db init
# flask db migrate
# flask db upgrade

# 注册蓝图
app.register_blueprint(qa_bp)
app.register_blueprint(auth_bp)

# 高版本flask则是修改这个配置解决中文乱码
app.json.ensure_ascii = False

if __name__ == "__main__":
    app.run(debug=True)