"""
用户互动 API：评分、收藏、评论、播放
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.interact_service import InteractService
from app.utils.response import success_response, error_response, page_response

interact_bp = Blueprint('interact', __name__)


# ========= 评分 =========
@interact_bp.route('/rate', methods=['POST'])
@jwt_required()
def rate_song():
    """给歌曲评分"""
    identity = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('songId')
    score = data.get('score')
    if not song_id or score is None:
        return error_response(400, '歌曲ID和评分不能为空')

    rating, err = InteractService.rate_song(identity['user_id'], song_id, score)
    if err:
        return error_response(400, err)
    return success_response(rating.to_dict(), '评分成功')


@interact_bp.route('/rating/<int:song_id>', methods=['GET'])
@jwt_required()
def get_my_rating(song_id):
    """获取我对某歌曲的评分"""
    identity = get_jwt_identity()
    rating = InteractService.get_user_rating(identity['user_id'], song_id)
    return success_response(rating.to_dict() if rating else None)


# ========= 收藏 =========
@interact_bp.route('/favorite', methods=['POST'])
@jwt_required()
def toggle_favorite():
    """收藏/取消收藏"""
    identity = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('songId')
    if not song_id:
        return error_response(400, '歌曲ID不能为空')

    ok, msg, is_fav = InteractService.toggle_favorite(identity['user_id'], song_id)
    if not ok:
        return error_response(400, msg)
    return success_response({'isFavorited': is_fav}, msg)


@interact_bp.route('/favorite/check/<int:song_id>', methods=['GET'])
@jwt_required()
def check_favorite(song_id):
    """检查是否已收藏"""
    identity = get_jwt_identity()
    is_fav = InteractService.is_favorited(identity['user_id'], song_id)
    return success_response({'isFavorited': is_fav})


# ========= 评论 =========
@interact_bp.route('/comment', methods=['POST'])
@jwt_required()
def add_comment():
    """添加评论"""
    identity = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('songId')
    content = data.get('content', '').strip()
    parent_id = data.get('parentId')

    if not song_id or not content:
        return error_response(400, '歌曲ID和评论内容不能为空')

    comment, err = InteractService.add_comment(identity['user_id'], song_id, content, parent_id)
    if err:
        return error_response(400, err)
    return success_response(comment.to_dict(), '评论成功')


@interact_bp.route('/comments/<int:song_id>', methods=['GET'])
def get_comments(song_id):
    """获取歌曲评论"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    items, total = InteractService.get_song_comments(song_id, page, page_size)
    return page_response(items, total, page, page_size)


@interact_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """删除评论"""
    identity = get_jwt_identity()
    ok, err = InteractService.delete_comment(comment_id, identity['user_id'])
    if not ok:
        return error_response(400, err)
    return success_response(message='评论已删除')


# ========= 播放 =========
@interact_bp.route('/play', methods=['POST'])
@jwt_required()
def record_play():
    """记录播放"""
    identity = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('songId')
    duration = data.get('duration', 0)

    if not song_id:
        return error_response(400, '歌曲ID不能为空')

    history, err = InteractService.record_play(identity['user_id'], song_id, duration)
    if err:
        return error_response(400, err)
    return success_response(history.to_dict())
