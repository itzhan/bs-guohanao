"""
用户互动模型：评分、收藏、评论、播放记录
"""
from datetime import datetime
from app.extensions import db


class Rating(db.Model):
    """用户评分表"""
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False, comment='歌曲ID')
    score = db.Column(db.Float, nullable=False, comment='评分(1-5)')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', name='uq_user_song_rating'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'songId': self.song_id,
            'score': self.score,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False, comment='歌曲ID')
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', name='uq_user_song_fav'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'songId': self.song_id,
            'songTitle': self.song.title if self.song else None,
            'songCover': self.song.cover_image if self.song else None,
            'artistName': self.song.artist.name if self.song and self.song.artist else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False, comment='歌曲ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), comment='父评论ID(回复)')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    sentiment_score = db.Column(db.Float, comment='情感得分(0-1)')
    sentiment_label = db.Column(db.String(20), comment='情感标签：正向/中性/负向')
    status = db.Column(db.SmallInteger, default=1, comment='状态：0-隐藏 1-正常')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 自引用关系
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side='Comment.id'), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'username': self.user.nickname or self.user.username if self.user else None,
            'userAvatar': self.user.avatar if self.user else None,
            'songId': self.song_id,
            'content': self.content,
            'parentId': self.parent_id,
            'likeCount': self.like_count,
            'sentimentScore': self.sentiment_score,
            'sentimentLabel': self.sentiment_label,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class PlayHistory(db.Model):
    """播放记录表"""
    __tablename__ = 'play_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False, comment='歌曲ID')
    play_duration = db.Column(db.Integer, default=0, comment='播放时长(秒)')
    play_count = db.Column(db.Integer, default=1, comment='播放次数')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'songId': self.song_id,
            'songTitle': self.song.title if self.song else None,
            'songCover': self.song.cover_image if self.song else None,
            'artistName': self.song.artist.name if self.song and self.song.artist else None,
            'playDuration': self.play_duration,
            'playCount': self.play_count,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
