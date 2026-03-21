"""
推荐 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.recommend_service import RecommendService
from app.utils.response import success_response, error_response

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/personal', methods=['GET'])
@jwt_required()
def get_personal_recommendations():
    """获取个性化推荐"""
    identity = get_jwt_identity()
    limit = request.args.get('limit', 20, type=int)
    recs = RecommendService.get_recommendations(identity['user_id'], limit)
    return success_response(recs)


@recommend_bp.route('/similar/<int:song_id>', methods=['GET'])
def get_similar_songs(song_id):
    """获取相似歌曲推荐"""
    limit = request.args.get('limit', 10, type=int)
    songs = RecommendService.get_similar_songs(song_id, limit)
    return success_response(songs)
