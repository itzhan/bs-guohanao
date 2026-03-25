"""
推荐策略管理服务
"""
import json
from sqlalchemy import func
from app.extensions import db, redis_client
from app.models.recommend import Recommendation
from app.models.interact import Rating, PlayHistory, Favorite
from app.models.song import Song


# 默认推荐策略配置
DEFAULT_CONFIG = {
    'alsMaxIter': 15,
    'alsRank': 20,
    'alsRegParam': 0.1,
    'timeDecayBase': 0.9,
    'timeDecayUnit': 30,
    'playWeight': 0.6,
    'durationWeight': 0.4,
    'favoriteBonus': 0.5,
    'coldStartEnabled': True,
    'hotFallbackEnabled': True,
    'recommendLimit': 20,
}

CONFIG_KEY = 'recommend:strategy:config'


class StrategyService:

    @staticmethod
    def get_config():
        """获取当前推荐策略配置"""
        try:
            cached = redis_client.get(CONFIG_KEY)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return DEFAULT_CONFIG.copy()

    @staticmethod
    def update_config(data):
        """更新推荐策略配置"""
        config = StrategyService.get_config()
        for k, v in data.items():
            if k in config:
                config[k] = v
        try:
            redis_client.set(CONFIG_KEY, json.dumps(config), ex=86400 * 30)
        except Exception:
            pass
        return config

    @staticmethod
    def get_metrics():
        """获取推荐效果指标"""
        # 总推荐记录数
        total_recs = Recommendation.query.count()

        # 已查看推荐数
        read_recs = Recommendation.query.filter_by(is_read=1).count()

        # 覆盖率：被推荐的歌曲数 / 总歌曲数
        rec_songs = db.session.query(func.count(func.distinct(Recommendation.song_id))).scalar() or 0
        total_songs = Song.query.filter(Song.status == 1).count() or 1
        coverage = round(rec_songs / total_songs * 100, 1)

        # 被推荐用户数 / 总用户数
        rec_users = db.session.query(func.count(func.distinct(Recommendation.user_id))).scalar() or 0

        # 推荐后用户的实际行为（推荐的歌曲被评分/收藏/播放的比例）
        rec_song_ids = db.session.query(func.distinct(Recommendation.song_id)).subquery()

        # 推荐歌曲被评分的数量
        rated_recs = db.session.query(func.count(func.distinct(Rating.song_id))) \
            .filter(Rating.song_id.in_(db.session.query(rec_song_ids))).scalar() or 0

        # 推荐歌曲被播放的数量
        played_recs = db.session.query(func.count(func.distinct(PlayHistory.song_id))) \
            .filter(PlayHistory.song_id.in_(db.session.query(rec_song_ids))).scalar() or 0

        # 推荐分数分布
        score_ranges = [
            ('高匹配(4-5分)', 4.0, 5.0),
            ('中匹配(3-4分)', 3.0, 4.0),
            ('低匹配(2-3分)', 2.0, 3.0),
            ('极低(<2分)', 0, 2.0),
        ]
        score_dist = []
        for label, low, high in score_ranges:
            count = Recommendation.query.filter(
                Recommendation.score >= low,
                Recommendation.score < high if high < 5.0 else Recommendation.score <= high
            ).count()
            score_dist.append({'name': label, 'value': count})

        # 算法分布
        algo_dist = db.session.query(
            Recommendation.algorithm,
            func.count(Recommendation.id).label('count')
        ).group_by(Recommendation.algorithm).all()

        return {
            'totalRecommendations': total_recs,
            'readRecommendations': read_recs,
            'readRate': round(read_recs / total_recs * 100, 1) if total_recs else 0,
            'coverageRate': coverage,
            'coveredSongs': rec_songs,
            'coveredUsers': rec_users,
            'ratedAfterRec': rated_recs,
            'playedAfterRec': played_recs,
            'scoreDistribution': score_dist,
            'algorithmDistribution': [{'name': a or 'unknown', 'value': c} for a, c in algo_dist],
        }
