"""
管理端 API
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.admin_service import AdminService
from app.services.song_service import GenreService
from app.utils.response import success_response, error_response, page_response
from app.utils.auth import admin_required, operator_required

admin_bp = Blueprint('admin', __name__)


# ========= 用户管理 =========
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword')
    role = request.args.get('role')
    status = request.args.get('status', type=int)
    items, total = AdminService.get_users(page, page_size, keyword, role, status)
    return page_response(items, total, page, page_size)


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """启用/禁用用户"""
    data = request.get_json()
    status = data.get('status')
    if status not in (0, 1):
        return error_response(400, '状态值无效')
    ok, err = AdminService.update_user_status(user_id, status)
    if not ok:
        return error_response(400, err)
    return success_response(message='操作成功')


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """修改用户角色"""
    data = request.get_json()
    role = data.get('role')
    ok, err = AdminService.update_user_role(user_id, role)
    if not ok:
        return error_response(400, err)
    return success_response(message='角色修改成功')


# ========= 歌曲管理 =========
@admin_bp.route('/songs', methods=['GET'])
@operator_required
def get_songs():
    """管理端获取歌曲列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword')
    status = request.args.get('status', type=int)
    items, total = AdminService.get_all_songs(page, page_size, keyword, status)
    return page_response(items, total, page, page_size)


@admin_bp.route('/songs', methods=['POST'])
@operator_required
def create_song():
    """新增歌曲"""
    data = request.get_json()
    if not data.get('title') or not data.get('artistId'):
        return error_response(400, '歌曲名和歌手不能为空')
    song = AdminService.create_song(data)
    return success_response(song.to_dict(), '歌曲添加成功')


@admin_bp.route('/songs/<int:song_id>', methods=['PUT'])
@operator_required
def update_song(song_id):
    """更新歌曲"""
    data = request.get_json()
    song, err = AdminService.update_song(song_id, data)
    if err:
        return error_response(400, err)
    return success_response(song.to_dict(), '歌曲更新成功')


@admin_bp.route('/songs/<int:song_id>', methods=['DELETE'])
@operator_required
def delete_song(song_id):
    """删除/下架歌曲"""
    ok, err = AdminService.delete_song(song_id)
    if not ok:
        return error_response(400, err)
    return success_response(message='歌曲已下架')


# ========= 歌手管理 =========
@admin_bp.route('/artists', methods=['POST'])
@operator_required
def create_artist():
    """新增歌手"""
    data = request.get_json()
    if not data.get('name'):
        return error_response(400, '歌手名不能为空')
    artist = AdminService.create_artist(data)
    return success_response(artist.to_dict(), '歌手添加成功')


@admin_bp.route('/artists/<int:artist_id>', methods=['PUT'])
@operator_required
def update_artist(artist_id):
    """更新歌手"""
    data = request.get_json()
    artist, err = AdminService.update_artist(artist_id, data)
    if err:
        return error_response(400, err)
    return success_response(artist.to_dict(), '歌手更新成功')


@admin_bp.route('/artists/<int:artist_id>', methods=['DELETE'])
@admin_required
def delete_artist(artist_id):
    """删除歌手"""
    ok, err = AdminService.delete_artist(artist_id)
    if not ok:
        return error_response(400, err)
    return success_response(message='歌手已删除')


# ========= 流派管理 =========
@admin_bp.route('/genres', methods=['POST'])
@operator_required
def create_genre():
    """新增流派"""
    data = request.get_json()
    if not data.get('name'):
        return error_response(400, '流派名不能为空')
    genre, err = AdminService.create_genre(data)
    if err:
        return error_response(400, err)
    return success_response(genre.to_dict(), '流派添加成功')


@admin_bp.route('/genres/<int:genre_id>', methods=['DELETE'])
@admin_required
def delete_genre(genre_id):
    """删除流派"""
    ok, err = AdminService.delete_genre(genre_id)
    if not ok:
        return error_response(400, err)
    return success_response(message='流派已删除')


# ========= 评论管理 =========
@admin_bp.route('/comments', methods=['GET'])
@operator_required
def get_comments():
    """获取评论列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    status = request.args.get('status', type=int)
    items, total = AdminService.get_comments(page, page_size, status)
    return page_response(items, total, page, page_size)


@admin_bp.route('/comments/<int:comment_id>/status', methods=['PUT'])
@operator_required
def update_comment_status(comment_id):
    """审核评论"""
    data = request.get_json()
    status = data.get('status')
    if status not in (0, 1):
        return error_response(400, '状态值无效')
    ok, err = AdminService.update_comment_status(comment_id, status)
    if not ok:
        return error_response(400, err)
    return success_response(message='评论状态已更新')


# ========= 操作日志 =========
@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    """获取操作日志"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    module = request.args.get('module')
    items, total = AdminService.get_operation_logs(page, page_size, module)
    return page_response(items, total, page, page_size)
