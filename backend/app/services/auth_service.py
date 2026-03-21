"""
用户认证服务
"""
from datetime import datetime
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User


class AuthService:

    @staticmethod
    def register(username, password, nickname=None, email=None, phone=None):
        """用户注册"""
        if User.query.filter_by(username=username).first():
            return None, '用户名已存在'

        user = User(
            username=username,
            nickname=nickname or username,
            email=email,
            phone=phone,
            role='user',
            status=1,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login(username, password):
        """用户登录"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None, None, '用户不存在'
        if user.status == 0:
            return None, None, '账号已被禁用'
        if not user.check_password(password):
            return None, None, '密码错误'

        # 更新最后登录时间
        user.last_login = datetime.now()
        db.session.commit()

        # 生成 JWT Token
        identity = {'user_id': user.id, 'username': user.username, 'role': user.role}
        token = create_access_token(identity=identity)
        return user, token, None

    @staticmethod
    def get_user_info(user_id):
        """获取用户信息"""
        return User.query.get(user_id)

    @staticmethod
    def update_user_info(user_id, **kwargs):
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None, '用户不存在'

        allowed_fields = ['nickname', 'email', 'phone', 'avatar', 'gender', 'age']
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)

        db.session.commit()
        return user, None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        user = User.query.get(user_id)
        if not user:
            return False, '用户不存在'
        if not user.check_password(old_password):
            return False, '原密码错误'

        user.set_password(new_password)
        db.session.commit()
        return True, None
