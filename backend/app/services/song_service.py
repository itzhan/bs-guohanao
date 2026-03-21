"""
歌曲服务
"""
from app.extensions import db
from app.models.song import Song, Artist, Album, Genre, song_genre


class SongService:

    @staticmethod
    def get_song_list(page=1, page_size=10, keyword=None, genre_id=None,
                      artist_id=None, language=None, sort_by='created_at'):
        """获取歌曲列表（分页 + 筛选）"""
        query = Song.query.filter(Song.status == 1)

        if keyword:
            query = query.filter(
                db.or_(
                    Song.title.like(f'%{keyword}%'),
                    Song.lyrics.like(f'%{keyword}%')
                )
            )
        if genre_id:
            query = query.filter(Song.genres.any(Genre.id == genre_id))
        if artist_id:
            query = query.filter(Song.artist_id == artist_id)
        if language:
            query = query.filter(Song.language == language)

        # 排序
        sort_map = {
            'created_at': Song.created_at.desc(),
            'play_count': Song.play_count.desc(),
            'avg_rating': Song.avg_rating.desc(),
            'favorite_count': Song.favorite_count.desc(),
        }
        order = sort_map.get(sort_by, Song.created_at.desc())
        query = query.order_by(order)

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [s.to_simple_dict() for s in pagination.items]
        return items, pagination.total

    @staticmethod
    def get_song_detail(song_id):
        """获取歌曲详情"""
        return Song.query.get(song_id)

    @staticmethod
    def get_hot_songs(limit=20):
        """获取热门歌曲"""
        songs = Song.query.filter(Song.status == 1) \
            .order_by(Song.play_count.desc()) \
            .limit(limit).all()
        return [s.to_simple_dict() for s in songs]

    @staticmethod
    def get_new_songs(limit=20):
        """获取最新歌曲"""
        songs = Song.query.filter(Song.status == 1) \
            .order_by(Song.created_at.desc()) \
            .limit(limit).all()
        return [s.to_simple_dict() for s in songs]

    @staticmethod
    def get_top_rated(limit=20):
        """获取高评分歌曲"""
        songs = Song.query.filter(Song.status == 1, Song.rating_count >= 5) \
            .order_by(Song.avg_rating.desc()) \
            .limit(limit).all()
        return [s.to_simple_dict() for s in songs]

    @staticmethod
    def search_songs(keyword, page=1, page_size=10):
        """搜索歌曲（标题、歌手、歌词）"""
        query = Song.query.filter(Song.status == 1).join(Artist).filter(
            db.or_(
                Song.title.like(f'%{keyword}%'),
                Artist.name.like(f'%{keyword}%'),
                Song.lyrics.like(f'%{keyword}%')
            )
        )
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [s.to_simple_dict() for s in pagination.items]
        return items, pagination.total


class ArtistService:

    @staticmethod
    def get_artist_list(page=1, page_size=10, region=None, keyword=None):
        """获取歌手列表"""
        query = Artist.query
        if region:
            query = query.filter(Artist.region == region)
        if keyword:
            query = query.filter(Artist.name.like(f'%{keyword}%'))
        query = query.order_by(Artist.fans_count.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [a.to_dict() for a in pagination.items]
        return items, pagination.total

    @staticmethod
    def get_artist_detail(artist_id):
        """获取歌手详情"""
        return Artist.query.get(artist_id)


class AlbumService:

    @staticmethod
    def get_album_list(page=1, page_size=10, artist_id=None):
        """获取专辑列表"""
        query = Album.query
        if artist_id:
            query = query.filter(Album.artist_id == artist_id)
        query = query.order_by(Album.release_date.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [a.to_dict() for a in pagination.items]
        return items, pagination.total


class GenreService:

    @staticmethod
    def get_all_genres():
        """获取所有流派"""
        genres = Genre.query.all()
        return [g.to_dict() for g in genres]
