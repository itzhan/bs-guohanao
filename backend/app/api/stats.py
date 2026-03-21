"""
数据统计分析 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.stats_service import StatsService
from app.utils.response import success_response
from app.utils.auth import operator_required

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview', methods=['GET'])
def get_overview():
    """系统概览"""
    return success_response(StatsService.get_overview())


@stats_bp.route('/rating-distribution', methods=['GET'])
def get_rating_distribution():
    """评分分布"""
    return success_response(StatsService.get_rating_distribution())


@stats_bp.route('/genre-distribution', methods=['GET'])
def get_genre_distribution():
    """流派占比"""
    return success_response(StatsService.get_genre_distribution())


@stats_bp.route('/play-trend', methods=['GET'])
def get_play_trend():
    """播放趋势"""
    days = request.args.get('days', 30, type=int)
    return success_response(StatsService.get_play_trend(days))


@stats_bp.route('/user-stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """用户个人数据分析"""
    identity = get_jwt_identity()
    return success_response(StatsService.get_user_preference_stats(identity['user_id']))


@stats_bp.route('/top-artists', methods=['GET'])
def get_top_artists():
    """热门歌手排行"""
    limit = request.args.get('limit', 10, type=int)
    return success_response(StatsService.get_top_artists(limit))


@stats_bp.route('/language-distribution', methods=['GET'])
def get_language_distribution():
    """语言分布"""
    return success_response(StatsService.get_language_distribution())
