"""
音乐相关模型：歌曲、歌手、专辑、流派
"""
from datetime import datetime
from app.extensions import db


# 歌曲-流派多对多关联表
song_genre = db.Table(
    'song_genre',
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class Genre(db.Model):
    """流派/分类表"""
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='流派名称')
    description = db.Column(db.String(255), comment='流派描述')
    cover_image = db.Column(db.String(255), comment='流派封面图')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coverImage': self.cover_image,
        }


class Artist(db.Model):
    """歌手/艺术家表"""
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='歌手名')
    avatar = db.Column(db.String(255), comment='歌手头像')
    region = db.Column(db.String(50), comment='地区：华语/欧美/日韩/其他')
    description = db.Column(db.Text, comment='歌手简介')
    fans_count = db.Column(db.Integer, default=0, comment='粉丝数')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    songs = db.relationship('Song', backref='artist', lazy='dynamic')
    albums = db.relationship('Album', backref='artist', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'region': self.region,
            'description': self.description,
            'fansCount': self.fans_count,
        }


class Album(db.Model):
    """专辑表"""
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, comment='专辑名')
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False, comment='歌手ID')
    cover_image = db.Column(db.String(255), comment='专辑封面')
    release_date = db.Column(db.Date, comment='发行日期')
    description = db.Column(db.Text, comment='专辑简介')
    song_count = db.Column(db.Integer, default=0, comment='歌曲数')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    songs = db.relationship('Song', backref='album', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'artistId': self.artist_id,
            'artistName': self.artist.name if self.artist else None,
            'coverImage': self.cover_image,
            'releaseDate': self.release_date.isoformat() if self.release_date else None,
            'description': self.description,
            'songCount': self.song_count,
        }


class Song(db.Model):
    """歌曲表"""
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='歌曲名')
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False, comment='歌手ID')
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), comment='专辑ID')
    duration = db.Column(db.Integer, comment='时长(秒)')
    cover_image = db.Column(db.String(255), comment='封面图')
    audio_url = db.Column(db.String(255), comment='音频URL')
    lyrics = db.Column(db.Text, comment='歌词')
    release_date = db.Column(db.Date, comment='发行日期')
    language = db.Column(db.String(20), comment='语言：中文/英文/日文/韩文/其他')
    avg_rating = db.Column(db.Float, default=0.0, comment='平均评分')
    rating_count = db.Column(db.Integer, default=0, comment='评分人数')
    play_count = db.Column(db.Integer, default=0, comment='播放次数')
    favorite_count = db.Column(db.Integer, default=0, comment='收藏次数')
    status = db.Column(db.SmallInteger, default=1, comment='状态：0-下架 1-正常')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 多对多关系
    genres = db.relationship('Genre', secondary=song_genre, backref=db.backref('songs', lazy='dynamic'))

    # 关系
    ratings = db.relationship('Rating', backref='song', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='song', lazy='dynamic')
    comments = db.relationship('Comment', backref='song', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artistId': self.artist_id,
            'artistName': self.artist.name if self.artist else None,
            'albumId': self.album_id,
            'albumName': self.album.name if self.album else None,
            'duration': self.duration,
            'coverImage': self.cover_image,
            'audioUrl': self.audio_url,
            'lyrics': self.lyrics,
            'releaseDate': self.release_date.isoformat() if self.release_date else None,
            'language': self.language,
            'avgRating': self.avg_rating,
            'ratingCount': self.rating_count,
            'playCount': self.play_count,
            'favoriteCount': self.favorite_count,
            'genres': [g.to_dict() for g in self.genres],
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    def to_simple_dict(self):
        """简要信息（列表展示用）"""
        return {
            'id': self.id,
            'title': self.title,
            'artistId': self.artist_id,
            'artistName': self.artist.name if self.artist else None,
            'coverImage': self.cover_image,
            'duration': self.duration,
            'avgRating': self.avg_rating,
            'playCount': self.play_count,
            'genres': [g.name for g in self.genres],
        }
