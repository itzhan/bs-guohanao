"""
系统管理模型：操作日志
"""
from datetime import datetime
from app.extensions import db


class OperationLog(db.Model):
    """操作日志表"""
    __tablename__ = 'operation_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='操作用户ID')
    username = db.Column(db.String(50), comment='操作用户名')
    action = db.Column(db.String(100), nullable=False, comment='操作类型')
    module = db.Column(db.String(50), comment='操作模块')
    description = db.Column(db.Text, comment='操作描述')
    ip_address = db.Column(db.String(50), comment='IP地址')
    request_method = db.Column(db.String(10), comment='请求方法')
    request_url = db.Column(db.String(255), comment='请求URL')
    status = db.Column(db.SmallInteger, default=1, comment='操作状态：0-失败 1-成功')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    user = db.relationship('User', backref=db.backref('operation_logs', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'username': self.username,
            'action': self.action,
            'module': self.module,
            'description': self.description,
            'ipAddress': self.ip_address,
            'requestMethod': self.request_method,
            'requestUrl': self.request_url,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
