"""
数据统计分析服务
"""
from sqlalchemy import func, extract
from app.extensions import db
from app.models.user import User
from app.models.song import Song, Genre, Artist, song_genre
from app.models.interact import Rating, PlayHistory, Favorite, Comment


class StatsService:

    @staticmethod
    def get_overview():
        """获取系统概览数据"""
        return {
            'totalUsers': User.query.filter(User.role == 'user').count(),
            'totalSongs': Song.query.filter(Song.status == 1).count(),
            'totalArtists': Artist.query.count(),
            'totalRatings': Rating.query.count(),
            'totalPlays': db.session.query(func.sum(Song.play_count)).scalar() or 0,
            'totalComments': Comment.query.filter(Comment.status == 1).count(),
        }

    @staticmethod
    def get_rating_distribution():
        """获取评分分布统计"""
        results = db.session.query(
            func.floor(Rating.score).label('score'),
            func.count(Rating.id).label('count')
        ).group_by(func.floor(Rating.score)).all()

        distribution = {str(i): 0 for i in range(1, 6)}
        for row in results:
            key = str(int(row.score))
            if key in distribution:
                distribution[key] = row.count
        return distribution

    @staticmethod
    def get_genre_distribution():
        """获取流派占比统计"""
        results = db.session.query(
            Genre.name,
            func.count(song_genre.c.song_id).label('count')
        ).join(song_genre, Genre.id == song_genre.c.genre_id) \
            .group_by(Genre.name) \
            .order_by(func.count(song_genre.c.song_id).desc()) \
            .all()

        return [{'name': name, 'value': count} for name, count in results]

    @staticmethod
    def get_play_trend(days=30):
        """获取播放趋势（按日）"""
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)

        results = db.session.query(
            func.date(PlayHistory.created_at).label('date'),
            func.count(PlayHistory.id).label('count')
        ).filter(PlayHistory.created_at >= start_date) \
            .group_by(func.date(PlayHistory.created_at)) \
            .order_by(func.date(PlayHistory.created_at)) \
            .all()

        return [{'date': str(row.date), 'count': row.count} for row in results]

    @staticmethod
    def get_user_preference_stats(user_id):
        """获取用户个人偏好统计"""
        # 用户的流派偏好（根据播放和评分）
        genre_stats = db.session.query(
            Genre.name,
            func.count().label('count')
        ).join(song_genre, Genre.id == song_genre.c.genre_id) \
            .join(Song, Song.id == song_genre.c.song_id) \
            .join(PlayHistory, PlayHistory.song_id == Song.id) \
            .filter(PlayHistory.user_id == user_id) \
            .group_by(Genre.name) \
            .order_by(func.count().desc()) \
            .limit(10).all()

        # 用户的评分分布
        rating_stats = db.session.query(
            func.floor(Rating.score).label('score'),
            func.count(Rating.id).label('count')
        ).filter(Rating.user_id == user_id) \
            .group_by(func.floor(Rating.score)).all()

        # 用户活跃时段
        hour_stats = db.session.query(
            extract('hour', PlayHistory.created_at).label('hour'),
            func.count(PlayHistory.id).label('count')
        ).filter(PlayHistory.user_id == user_id) \
            .group_by(extract('hour', PlayHistory.created_at)) \
            .order_by(extract('hour', PlayHistory.created_at)) \
            .all()

        return {
            'genrePreference': [{'name': name, 'value': count} for name, count in genre_stats],
            'ratingDistribution': {str(int(row.score)): row.count for row in rating_stats},
            'activeHours': [{'hour': int(row.hour), 'count': row.count} for row in hour_stats],
            'totalPlays': PlayHistory.query.filter_by(user_id=user_id).count(),
            'totalFavorites': Favorite.query.filter_by(user_id=user_id).count(),
            'totalRatings': Rating.query.filter_by(user_id=user_id).count(),
        }

    @staticmethod
    def get_top_artists(limit=10):
        """获取热门歌手排行"""
        results = db.session.query(
            Artist.id, Artist.name, Artist.avatar,
            func.sum(Song.play_count).label('total_plays')
        ).join(Song, Song.artist_id == Artist.id) \
            .filter(Song.status == 1) \
            .group_by(Artist.id, Artist.name, Artist.avatar) \
            .order_by(func.sum(Song.play_count).desc()) \
            .limit(limit).all()

        return [{
            'id': r.id,
            'name': r.name,
            'avatar': r.avatar,
            'totalPlays': int(r.total_plays) if r.total_plays else 0
        } for r in results]

    @staticmethod
    def get_language_distribution():
        """获取语言分布"""
        results = db.session.query(
            Song.language,
            func.count(Song.id).label('count')
        ).filter(Song.status == 1, Song.language.isnot(None)) \
            .group_by(Song.language) \
            .order_by(func.count(Song.id).desc()) \
            .all()

        return [{'name': lang or '未知', 'value': count} for lang, count in results]
