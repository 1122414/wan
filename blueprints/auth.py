from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models import UserModel as User
from exts import db
from exts import mail
from exts import redis
from flask_mail import Message
import string
import random
from models import EmailCaptchaModel
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # 验证用户名/邮箱和密码
        user = User.query.filter(User.username == username).first()
        if not user:
            # 尝试用邮箱登录
            user = User.query.filter(User.email == username).first()
        
        if user and check_password_hash(user.password, password):
            # 登录成功，设置session
            session['user_id'] = user.id
            session['username'] = user.username
            
            # 如果勾选了记住我，设置session的过期时间更长
            if remember:
                session.permanent = True
                
            return jsonify({'code': 200, 'msg': '登录成功'})
        else:
            # 登录失败
            return jsonify({'code': 400, 'msg': '账号或密码错误，请重试'})
    
    return render_template('login.html')

# region
# @bp.route('/captcha/email')
# def get_email_captcha():
#     '''
#     学习版本
#     '''
#     # /captcha/email/<email>
#     # /captcha/email?email=xxx@qq.com
#     email = request.args.get('email')
#     # email = '2112433073@e.gzhu.edu.cn'
#     # 4/6位随机验证码
#     # string.digits*4:0123456789 0123456789 0123456789 0123456789
#     source = string.digits*4
#     # 随机取四位 random.sample(source, 4):从source中随机取4个元素
#     captcha = random.sample(source, 4)
#     # 空字符串作为连接符（表示直接拼接，不添加其他字符），字符串方法，将列表元素按顺序拼接
#     # '-'.join(captcha) → "H-e-l-l-o"  # 用连字符连接
#     # ''.join(captcha)  → "Hello"  
#     code = ''.join(captcha)
#     mail.send_message(subject='验证码', recipients=[email], body=f'您的验证码是{code}')
#     # 存储验证码  memcached/redis
#     # 用数据库存储
#     email_captcha = EmailCaptchaModel(email=email, captcha=code)
#     db.session.add(email_captcha)
#     db.session.commit()
#     # RESTful API
#     # {code: 200/400/500, msg: '', data: {}}
#     return jsonify({'code':200,'msg': 'ok', 'data':None})
# endregion

# region
@bp.route('/captcha/email')
def get_email_captcha():
    '''
    重写版本
    '''
    email = request.args.get('email')
    print(f'当前email为：{email}')
    code = ''.join(random.sample(string.digits*4,4))
    try:
        redis.setex(f'captcha:{email}', 300, code)
        mail.send_message(
            subject='验证码', 
            recipients=[email], 
            body=f'您的验证码是{code}，请注意，验证码将在五分钟后失效'
            )
        return jsonify({'code':200, 'msg':'验证码发送成功'})
    except Exception as e:
        print (f'邮件发送失败: {e}')
        return 'success!'

#endregion
    
# 在app.py添加测试路由
# @bp.route('/encoding_test')
# def encoding_test():
#     return jsonify({
#         'direct': '直接中文',
#         'unicode': '\u4e2d\u6587\u6e2c\u8a66'
#     }), 200, {'Content-Type': 'application/json; charset=utf-8'}

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 验证邮箱是否存在、正确
    # 验证验证码是否正确
    if request.method == "POST":
        data = request.form
        email = data.get('email')
        phone = data.get('phone')
        captcha = data.get('captcha')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')
        
        # 验证两次输入的密码是否一致
        if password != confirm_password:
            return jsonify({'code': 400, 'msg': '两次输入的密码不一致'})
        
        if not redis.exists(f'captcha:{email}'):
            return jsonify({'code': 400, 'msg': '验证码已过期'})
        if redis.get(f'captcha:{email}').decode() != captcha:
            return jsonify({'code': 400, 'msg': '验证码错误'})
        if User.query.filter_by(email=email).first():
            return jsonify({'code': 400, 'msg': '该邮箱已经被注册过了'})
        if User.query.filter_by(phone=phone).first():
            return jsonify({'code': 400, 'msg': '该手机号已经被注册过了'})
        
        # 创建新用户
        try:
            user = User(
                username=data.get('username'),
                password=generate_password_hash(password),
                email=email,
                phone=data.get('phone')
            )
            db.session.add(user)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '注册成功'})
            
        except Exception as e:
            db.session.rollback()
            print(f"注册失败：{str(e)}")
            return jsonify({'code': 500, 'msg': '注册失败，请检查后请稍后重试'})
        
    return render_template('register.html')

# @bp.route('/mail/test')
# def mail_test():
#     message = Message(subject='Hello World', recipients=['2112433073@e.gzhu.edu.cn'])
#     message.body = 'This is a test email sent from a Flask application.'
#     try:
#         mail.send(message)
#     except Exception as e:
#         print(f'邮件发送失败: {e}')
#     return '发送成功'
