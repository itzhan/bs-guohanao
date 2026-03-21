"""
认证与权限装饰器
"""
from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.utils.response import error_response


def admin_required(fn):
    """管理员权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if identity.get('role') not in ('admin',):
            return error_response(403, '需要管理员权限')
        return fn(*args, **kwargs)
    return wrapper


def operator_required(fn):
    """运营人员权限装饰器（运营 + 管理员）"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if identity.get('role') not in ('admin', 'operator'):
            return error_response(403, '需要运营人员权限')
        return fn(*args, **kwargs)
    return wrapper


def login_required(fn):
    """登录用户权限装饰器"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper


def get_current_user_id():
    """获取当前登录用户 ID"""
    identity = get_jwt_identity()
    if identity:
        return identity.get('user_id')
    return None


def get_current_user_role():
    """获取当前登录用户角色"""
    identity = get_jwt_identity()
    if identity:
        return identity.get('role')
    return None
