"""
歌曲相关 API
"""
from flask import Blueprint, request
from app.services.song_service import SongService, ArtistService, AlbumService, GenreService
from app.utils.response import success_response, error_response, page_response

song_bp = Blueprint('song', __name__)


@song_bp.route('', methods=['GET'])
def get_song_list():
    """获取歌曲列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword')
    genre_id = request.args.get('genreId', type=int)
    artist_id = request.args.get('artistId', type=int)
    language = request.args.get('language')
    sort_by = request.args.get('sortBy', 'created_at')

    items, total = SongService.get_song_list(
        page=page, page_size=page_size, keyword=keyword,
        genre_id=genre_id, artist_id=artist_id, language=language,
        sort_by=sort_by
    )
    return page_response(items, total, page, page_size)


@song_bp.route('/<int:song_id>', methods=['GET'])
def get_song_detail(song_id):
    """获取歌曲详情"""
    song = SongService.get_song_detail(song_id)
    if not song:
        return error_response(404, '歌曲不存在')
    return success_response(song.to_dict())


@song_bp.route('/hot', methods=['GET'])
def get_hot_songs():
    """获取热门歌曲"""
    limit = request.args.get('limit', 20, type=int)
    return success_response(SongService.get_hot_songs(limit))


@song_bp.route('/new', methods=['GET'])
def get_new_songs():
    """获取最新歌曲"""
    limit = request.args.get('limit', 20, type=int)
    return success_response(SongService.get_new_songs(limit))


@song_bp.route('/top-rated', methods=['GET'])
def get_top_rated():
    """获取高评分歌曲"""
    limit = request.args.get('limit', 20, type=int)
    return success_response(SongService.get_top_rated(limit))


@song_bp.route('/search', methods=['GET'])
def search_songs():
    """搜索歌曲"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return error_response(400, '请输入搜索关键词')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    items, total = SongService.search_songs(keyword, page, page_size)
    return page_response(items, total, page, page_size)


# ========= 歌手 =========
@song_bp.route('/artists', methods=['GET'])
def get_artists():
    """获取歌手列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    region = request.args.get('region')
    keyword = request.args.get('keyword')
    items, total = ArtistService.get_artist_list(page, page_size, region, keyword)
    return page_response(items, total, page, page_size)


@song_bp.route('/artists/<int:artist_id>', methods=['GET'])
def get_artist_detail(artist_id):
    """获取歌手详情"""
    artist = ArtistService.get_artist_detail(artist_id)
    if not artist:
        return error_response(404, '歌手不存在')
    return success_response(artist.to_dict())


# ========= 专辑 =========
@song_bp.route('/albums', methods=['GET'])
def get_albums():
    """获取专辑列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    artist_id = request.args.get('artistId', type=int)
    items, total = AlbumService.get_album_list(page, page_size, artist_id)
    return page_response(items, total, page, page_size)


# ========= 流派 =========
@song_bp.route('/genres', methods=['GET'])
def get_genres():
    """获取所有流派"""
    return success_response(GenreService.get_all_genres())
