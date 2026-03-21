"""
用户相关 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.services.interact_service import InteractService
from app.services.recommend_service import RecommendService
from app.utils.response import success_response, error_response, page_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取个人信息"""
    identity = get_jwt_identity()
    user = AuthService.get_user_info(identity['user_id'])
    if not user:
        return error_response(404, '用户不存在')
    return success_response(user.to_dict())


@user_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """获取收藏列表"""
    identity = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    items, total = InteractService.get_user_favorites(identity['user_id'], page, page_size)
    return page_response(items, total, page, page_size)


@user_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """获取播放历史"""
    identity = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    items, total = InteractService.get_user_history(identity['user_id'], page, page_size)
    return page_response(items, total, page, page_size)


@user_bp.route('/preference', methods=['GET'])
@jwt_required()
def get_preference():
    """获取用户偏好"""
    identity = get_jwt_identity()
    pref = RecommendService.get_user_preference(identity['user_id'])
    return success_response(pref.to_dict() if pref else None)


@user_bp.route('/preference', methods=['POST'])
@jwt_required()
def save_preference():
    """保存用户偏好问卷"""
    identity = get_jwt_identity()
    data = request.get_json()
    pref = RecommendService.save_user_preference(identity['user_id'], data)
    return success_response(pref.to_dict(), '偏好保存成功')
