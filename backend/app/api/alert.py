"""
异常行为预警 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.alert_service import AlertService
from app.utils.response import success_response
from app.utils.auth import admin_required

alert_bp = Blueprint('alert', __name__)


@alert_bp.route('/list', methods=['GET'])
@admin_required
def get_alerts():
    """获取预警列表"""
    days = request.args.get('days', 7, type=int)
    return success_response(AlertService.get_alerts(days))


@alert_bp.route('/stats', methods=['GET'])
@admin_required
def get_alert_stats():
    """预警概览统计"""
    return success_response(AlertService.get_stats())
