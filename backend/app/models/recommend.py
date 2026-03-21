"""
推荐相关模型：用户偏好问卷、推荐结果
"""
from datetime import datetime
from app.extensions import db


class UserPreference(db.Model):
    """用户偏好问卷表（冷启动用）"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, comment='用户ID')
    favorite_genres = db.Column(db.Text, comment='喜爱流派(JSON数组)')
    favorite_artists = db.Column(db.Text, comment='喜爱歌手(JSON数组)')
    listening_scenarios = db.Column(db.Text, comment='听歌场景(JSON数组): 通勤/学习/运动/睡前等')
    preferred_language = db.Column(db.String(50), comment='偏好语言')
    mood_preference = db.Column(db.String(100), comment='情绪偏好: 欢快/伤感/平静/激昂')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    user = db.relationship('User', backref=db.backref('preference', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'favoriteGenres': self.favorite_genres,
            'favoriteArtists': self.favorite_artists,
            'listeningScenarios': self.listening_scenarios,
            'preferredLanguage': self.preferred_language,
            'moodPreference': self.mood_preference,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class Recommendation(db.Model):
    """推荐结果缓存表（ALS 离线计算后写入）"""
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False, comment='推荐歌曲ID')
    score = db.Column(db.Float, comment='推荐得分')
    algorithm = db.Column(db.String(50), default='ALS', comment='算法类型: ALS/CF/CB/Hybrid')
    reason = db.Column(db.String(255), comment='推荐理由')
    is_read = db.Column(db.Boolean, default=False, comment='是否已查看')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    user = db.relationship('User', backref=db.backref('recommendations', lazy='dynamic'))
    song = db.relationship('Song', backref=db.backref('recommended_to', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', 'algorithm', name='uq_user_song_algo'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'songId': self.song_id,
            'song': self.song.to_simple_dict() if self.song else None,
            'score': self.score,
            'algorithm': self.algorithm,
            'reason': self.reason,
            'isRead': self.is_read,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
