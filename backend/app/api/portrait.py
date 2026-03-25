"""
用户画像分析 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.portrait_service import PortraitService
from app.utils.response import success_response, error_response
from app.utils.auth import operator_required

portrait_bp = Blueprint('portrait', __name__)


@portrait_bp.route('/overview', methods=['GET'])
@operator_required
def get_overview():
    """用户群体画像概览"""
    return success_response(PortraitService.get_overview())


@portrait_bp.route('/preferences', methods=['GET'])
@operator_required
def get_preferences():
    """全局用户偏好标签分布"""
    return success_response(PortraitService.get_preferences())


@portrait_bp.route('/activity', methods=['GET'])
@operator_required
def get_activity():
    """活跃度分析"""
    return success_response(PortraitService.get_activity())


@portrait_bp.route('/<int:user_id>', methods=['GET'])
@operator_required
def get_user_detail(user_id):
    """单用户画像详情"""
    data = PortraitService.get_user_detail(user_id)
    if data is None:
        return error_response(404, '用户不存在')
    return success_response(data)
