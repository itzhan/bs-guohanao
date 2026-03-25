"""
推荐策略管理 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services.strategy_service import StrategyService
from app.utils.response import success_response
from app.utils.auth import admin_required

strategy_bp = Blueprint('strategy', __name__)


@strategy_bp.route('/metrics', methods=['GET'])
@admin_required
def get_metrics():
    """获取推荐效果指标"""
    return success_response(StrategyService.get_metrics())


@strategy_bp.route('/config', methods=['GET'])
@admin_required
def get_config():
    """获取当前算法参数配置"""
    return success_response(StrategyService.get_config())


@strategy_bp.route('/config', methods=['PUT'])
@admin_required
def update_config():
    """更新算法参数"""
    data = request.get_json()
    config = StrategyService.update_config(data)
    return success_response(config, '策略配置已更新')
