"""
用户模型
"""
from datetime import datetime
from hashlib import sha256
from app.extensions import db


class User(db.Model):
    """用户表 - 支持三种角色：user/operator/admin"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(128), nullable=False, comment='SHA-256加密密码')
    nickname = db.Column(db.String(50), comment='昵称')
    email = db.Column(db.String(100), comment='邮箱')
    phone = db.Column(db.String(20), comment='手机号')
    avatar = db.Column(db.String(255), comment='头像URL')
    gender = db.Column(db.SmallInteger, default=0, comment='性别：0-未知 1-男 2-女')
    age = db.Column(db.Integer, comment='年龄')
    role = db.Column(db.String(20), default='user', nullable=False, comment='角色：user/operator/admin')
    status = db.Column(db.SmallInteger, default=1, comment='状态：0-禁用 1-正常')
    preference_tags = db.Column(db.Text, comment='音乐偏好标签(JSON)')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    play_history = db.relationship('PlayHistory', backref='user', lazy='dynamic')

    def set_password(self, raw_password):
        """SHA-256 加密密码"""
        self.password = sha256(raw_password.encode('utf-8')).hexdigest()

    def check_password(self, raw_password):
        """验证密码"""
        return self.password == sha256(raw_password.encode('utf-8')).hexdigest()

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'gender': self.gender,
            'age': self.age,
            'role': self.role,
            'status': self.status,
            'preferenceTags': self.preference_tags,
            'lastLogin': self.last_login.isoformat() if self.last_login else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def __repr__(self):
        return f'<User {self.username}>'
