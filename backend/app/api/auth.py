"""
认证相关 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return error_response(400, '请求数据为空')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return error_response(400, '用户名和密码不能为空')
    if len(username) < 3 or len(username) > 50:
        return error_response(400, '用户名长度需在3-50之间')
    if len(password) < 6:
        return error_response(400, '密码长度至少6位')

    user, err = AuthService.register(
        username=username,
        password=password,
        nickname=data.get('nickname'),
        email=data.get('email'),
        phone=data.get('phone'),
    )
    if err:
        return error_response(400, err)

    return success_response(user.to_dict(), '注册成功')


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return error_response(400, '请求数据为空')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return error_response(400, '用户名和密码不能为空')

    user, token, err = AuthService.login(username, password)
    if err:
        return error_response(400, err)

    return success_response({
        'token': token,
        'user': user.to_dict()
    }, '登录成功')


@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def get_info():
    """获取当前用户信息"""
    identity = get_jwt_identity()
    user = AuthService.get_user_info(identity['user_id'])
    if not user:
        return error_response(404, '用户不存在')
    return success_response(user.to_dict())


@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_info():
    """更新用户信息"""
    identity = get_jwt_identity()
    data = request.get_json()
    user, err = AuthService.update_user_info(identity['user_id'], **data)
    if err:
        return error_response(400, err)
    return success_response(user.to_dict(), '更新成功')


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """修改密码"""
    identity = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')
    if not old_password or not new_password:
        return error_response(400, '旧密码和新密码不能为空')
    if len(new_password) < 6:
        return error_response(400, '新密码长度至少6位')

    ok, err = AuthService.change_password(identity['user_id'], old_password, new_password)
    if not ok:
        return error_response(400, err)
    return success_response(message='密码修改成功')
