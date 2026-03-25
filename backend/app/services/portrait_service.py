"""
用户画像分析服务
"""
from sqlalchemy import func, extract, case
from app.extensions import db
from app.models.user import User
from app.models.song import Song, Genre, song_genre
from app.models.interact import Rating, PlayHistory, Favorite, Comment


class PortraitService:

    @staticmethod
    def get_overview():
        """用户群体画像概览"""
        # 性别分布
        gender_dist = db.session.query(
            case(
                (User.gender == 1, '男'),
                (User.gender == 2, '女'),
                else_='未知'
            ).label('gender'),
            func.count(User.id).label('count')
        ).filter(User.role == 'user') \
            .group_by('gender').all()

        # 角色分布
        role_dist = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()

        # 年龄分段分布
        age_dist = db.session.query(
            case(
                (User.age < 18, '18岁以下'),
                (User.age.between(18, 25), '18-25岁'),
                (User.age.between(26, 35), '26-35岁'),
                (User.age.between(36, 45), '36-45岁'),
                (User.age > 45, '45岁以上'),
                else_='未知'
            ).label('age_group'),
            func.count(User.id).label('count')
        ).filter(User.role == 'user') \
            .group_by('age_group').all()

        # 用户注册趋势 (最近12个月)
        from datetime import datetime, timedelta
        twelve_months_ago = datetime.now() - timedelta(days=365)
        reg_trend = db.session.query(
            func.date_format(User.created_at, '%Y-%m').label('month'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= twelve_months_ago) \
            .group_by('month') \
            .order_by('month').all()

        return {
            'genderDistribution': [{'name': g, 'value': c} for g, c in gender_dist],
            'roleDistribution': [{'name': r, 'value': c} for r, c in role_dist],
            'ageDistribution': [{'name': a, 'value': c} for a, c in age_dist],
            'registrationTrend': [{'month': m, 'count': c} for m, c in reg_trend],
        }

    @staticmethod
    def get_preferences():
        """全局用户偏好标签分布"""
        # 最受欢迎的流派 (按播放次数)
        genre_pref = db.session.query(
            Genre.name,
            func.count(PlayHistory.id).label('count')
        ).join(song_genre, Genre.id == song_genre.c.genre_id) \
            .join(Song, Song.id == song_genre.c.song_id) \
            .join(PlayHistory, PlayHistory.song_id == Song.id) \
            .group_by(Genre.name) \
            .order_by(func.count(PlayHistory.id).desc()) \
            .limit(15).all()

        # 语言偏好
        lang_pref = db.session.query(
            Song.language,
            func.sum(Song.play_count).label('plays')
        ).filter(Song.language.isnot(None)) \
            .group_by(Song.language) \
            .order_by(func.sum(Song.play_count).desc()).all()

        # 平均评分分布
        avg_rating = db.session.query(func.avg(Rating.score)).scalar() or 0
        total_active = db.session.query(func.count(func.distinct(PlayHistory.user_id))).scalar() or 0

        return {
            'genrePreference': [{'name': n, 'value': c} for n, c in genre_pref],
            'languagePreference': [{'name': l or '未知', 'value': int(p or 0)} for l, p in lang_pref],
            'avgRating': round(float(avg_rating), 2),
            'activeUsers': total_active,
        }

    @staticmethod
    def get_activity():
        """用户活跃度分析"""
        # 按小时分布
        hour_dist = db.session.query(
            extract('hour', PlayHistory.created_at).label('hour'),
            func.count(PlayHistory.id).label('count')
        ).group_by('hour').order_by('hour').all()

        # 按星期分布
        weekday_dist = db.session.query(
            func.dayofweek(PlayHistory.created_at).label('weekday'),
            func.count(PlayHistory.id).label('count')
        ).group_by('weekday').order_by('weekday').all()

        weekday_names = {1: '周日', 2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六'}

        # 日活趋势 (最近30天)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        daily_active = db.session.query(
            func.date(PlayHistory.created_at).label('date'),
            func.count(func.distinct(PlayHistory.user_id)).label('dau')
        ).filter(PlayHistory.created_at >= thirty_days_ago) \
            .group_by('date').order_by('date').all()

        return {
            'hourDistribution': [{'hour': int(h), 'count': c} for h, c in hour_dist],
            'weekdayDistribution': [{'name': weekday_names.get(int(w), f'Day{w}'), 'value': c} for w, c in weekday_dist],
            'dailyActiveUsers': [{'date': str(d), 'dau': c} for d, c in daily_active],
        }

    @staticmethod
    def get_user_detail(user_id):
        """单用户画像详情"""
        user = User.query.get(user_id)
        if not user:
            return None

        # 用户的流派偏好
        genre_stats = db.session.query(
            Genre.name,
            func.count().label('count')
        ).join(song_genre, Genre.id == song_genre.c.genre_id) \
            .join(Song, Song.id == song_genre.c.song_id) \
            .join(PlayHistory, PlayHistory.song_id == Song.id) \
            .filter(PlayHistory.user_id == user_id) \
            .group_by(Genre.name) \
            .order_by(func.count().desc()).limit(10).all()

        # 用户听歌时段
        hour_stats = db.session.query(
            extract('hour', PlayHistory.created_at).label('hour'),
            func.count(PlayHistory.id).label('count')
        ).filter(PlayHistory.user_id == user_id) \
            .group_by('hour').order_by('hour').all()

        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'gender': user.gender,
                'age': user.age,
                'role': user.role,
            },
            'genrePreference': [{'name': n, 'value': c} for n, c in genre_stats],
            'activeHours': [{'hour': int(h), 'count': c} for h, c in hour_stats],
            'totalPlays': PlayHistory.query.filter_by(user_id=user_id).count(),
            'totalFavorites': Favorite.query.filter_by(user_id=user_id).count(),
            'totalRatings': Rating.query.filter_by(user_id=user_id).count(),
            'totalComments': Comment.query.filter(Comment.user_id == user_id, Comment.status == 1).count(),
        }
