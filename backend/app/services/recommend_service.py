"""
推荐服务
"""
import json
from app.extensions import db, redis_client
from app.models.recommend import Recommendation, UserPreference
from app.models.song import Song, Genre
from app.models.interact import Rating, Favorite, PlayHistory


class RecommendService:

    @staticmethod
    def get_recommendations(user_id, limit=20):
        """获取用户的个性化推荐（优先从缓存/数据库读取 ALS 结果）"""
        # 尝试从 Redis 缓存读取
        cache_key = f'recommend:{user_id}'
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        # 从数据库读取 ALS 离线推荐结果
        recs = Recommendation.query.filter_by(user_id=user_id) \
            .order_by(Recommendation.score.desc()) \
            .limit(limit).all()

        if recs:
            result = [r.to_dict() for r in recs]
            # 缓存到 Redis（1小时）
            try:
                redis_client.set(cache_key, json.dumps(result, ensure_ascii=False), ex=3600)
            except Exception:
                pass
            return result

        # 没有 ALS 结果时，使用基于内容的推荐（冷启动策略）
        return RecommendService._content_based_recommend(user_id, limit)

    @staticmethod
    def _content_based_recommend(user_id, limit=20):
        """基于内容的推荐（冷启动 / ALS 结果不足时的后备策略）"""
        # 先检查用户偏好问卷
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if pref and pref.favorite_genres:
            try:
                genre_names = json.loads(pref.favorite_genres)
                genres = Genre.query.filter(Genre.name.in_(genre_names)).all()
                genre_ids = [g.id for g in genres]
                if genre_ids:
                    songs = Song.query.filter(Song.status == 1) \
                        .filter(Song.genres.any(Genre.id.in_(genre_ids))) \
                        .order_by(Song.avg_rating.desc()) \
                        .limit(limit).all()
                    return [s.to_simple_dict() for s in songs]
            except (json.JSONDecodeError, TypeError):
                pass

        # 再检查用户的历史偏好（通过评分、收藏推断）
        liked_genre_ids = RecommendService._infer_preferred_genres(user_id)
        if liked_genre_ids:
            # 排除已听过的歌曲
            played_ids = [h.song_id for h in PlayHistory.query.filter_by(user_id=user_id).all()]
            query = Song.query.filter(Song.status == 1) \
                .filter(Song.genres.any(Genre.id.in_(liked_genre_ids)))
            if played_ids:
                query = query.filter(~Song.id.in_(played_ids))
            songs = query.order_by(Song.avg_rating.desc()).limit(limit).all()
            if songs:
                return [s.to_simple_dict() for s in songs]

        # 最后兜底：热门歌曲
        songs = Song.query.filter(Song.status == 1) \
            .order_by(Song.play_count.desc()) \
            .limit(limit).all()
        return [s.to_simple_dict() for s in songs]

    @staticmethod
    def _infer_preferred_genres(user_id):
        """从用户评分和收藏中推断喜爱的流派"""
        # 评分 >= 4 的歌曲
        rated = Rating.query.filter(Rating.user_id == user_id, Rating.score >= 4).all()
        # 收藏的歌曲
        faved = Favorite.query.filter_by(user_id=user_id).all()

        song_ids = list(set([r.song_id for r in rated] + [f.song_id for f in faved]))
        if not song_ids:
            return []

        songs = Song.query.filter(Song.id.in_(song_ids)).all()
        genre_count = {}
        for song in songs:
            for genre in song.genres:
                genre_count[genre.id] = genre_count.get(genre.id, 0) + 1

        # 取出现次数最多的前5个流派
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return [g_id for g_id, _ in sorted_genres[:5]]

    @staticmethod
    def save_user_preference(user_id, data):
        """保存用户偏好问卷"""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id)
            db.session.add(pref)

        if 'favoriteGenres' in data:
            pref.favorite_genres = json.dumps(data['favoriteGenres'], ensure_ascii=False)
        if 'favoriteArtists' in data:
            pref.favorite_artists = json.dumps(data['favoriteArtists'], ensure_ascii=False)
        if 'listeningScenarios' in data:
            pref.listening_scenarios = json.dumps(data['listeningScenarios'], ensure_ascii=False)
        if 'preferredLanguage' in data:
            pref.preferred_language = data['preferredLanguage']
        if 'moodPreference' in data:
            pref.mood_preference = data['moodPreference']

        db.session.commit()

        # 清除推荐缓存
        try:
            redis_client.delete(f'recommend:{user_id}')
        except Exception:
            pass

        return pref

    @staticmethod
    def get_user_preference(user_id):
        """获取用户偏好"""
        return UserPreference.query.filter_by(user_id=user_id).first()

    @staticmethod
    def get_similar_songs(song_id, limit=10):
        """获取相似歌曲（基于流派和歌手）"""
        song = Song.query.get(song_id)
        if not song:
            return []

        genre_ids = [g.id for g in song.genres]
        query = Song.query.filter(Song.status == 1, Song.id != song_id)
        if genre_ids:
            query = query.filter(
                db.or_(
                    Song.genres.any(Genre.id.in_(genre_ids)),
                    Song.artist_id == song.artist_id
                )
            )
        else:
            query = query.filter(Song.artist_id == song.artist_id)

        songs = query.order_by(Song.avg_rating.desc()).limit(limit).all()
        return [s.to_simple_dict() for s in songs]
