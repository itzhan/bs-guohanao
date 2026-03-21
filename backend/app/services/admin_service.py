"""
管理端服务
"""
from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.song import Song, Artist, Album, Genre, song_genre
from app.models.interact import Comment
from app.models.system import OperationLog


class AdminService:

    # ========= 用户管理 =========
    @staticmethod
    def get_users(page=1, page_size=10, keyword=None, role=None, status=None):
        """获取用户列表"""
        query = User.query
        if keyword:
            query = query.filter(
                db.or_(User.username.like(f'%{keyword}%'), User.nickname.like(f'%{keyword}%'))
            )
        if role:
            query = query.filter(User.role == role)
        if status is not None:
            query = query.filter(User.status == status)
        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return [u.to_dict() for u in pagination.items], pagination.total

    @staticmethod
    def update_user_status(user_id, status):
        """启用/禁用用户"""
        user = User.query.get(user_id)
        if not user:
            return False, '用户不存在'
        user.status = status
        db.session.commit()
        return True, None

    @staticmethod
    def update_user_role(user_id, role):
        """修改用户角色"""
        if role not in ('user', 'operator', 'admin'):
            return False, '无效的角色'
        user = User.query.get(user_id)
        if not user:
            return False, '用户不存在'
        user.role = role
        db.session.commit()
        return True, None

    # ========= 歌曲管理 =========
    @staticmethod
    def create_song(data):
        """新增歌曲"""
        song = Song(
            title=data.get('title'),
            artist_id=data.get('artistId'),
            album_id=data.get('albumId'),
            duration=data.get('duration'),
            cover_image=data.get('coverImage'),
            audio_url=data.get('audioUrl'),
            lyrics=data.get('lyrics'),
            language=data.get('language'),
        )
        # 处理流派
        genre_ids = data.get('genreIds', [])
        if genre_ids:
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            song.genres = genres

        db.session.add(song)
        db.session.commit()
        return song

    @staticmethod
    def update_song(song_id, data):
        """更新歌曲"""
        song = Song.query.get(song_id)
        if not song:
            return None, '歌曲不存在'

        fields = ['title', 'duration', 'cover_image', 'audio_url', 'lyrics', 'language', 'status']
        field_map = {'coverImage': 'cover_image', 'audioUrl': 'audio_url', 'artistId': 'artist_id', 'albumId': 'album_id'}

        for key, value in data.items():
            attr = field_map.get(key, key)
            if hasattr(song, attr) and value is not None:
                setattr(song, attr, value)

        genre_ids = data.get('genreIds')
        if genre_ids is not None:
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            song.genres = genres

        db.session.commit()
        return song, None

    @staticmethod
    def delete_song(song_id):
        """删除歌曲（软删，设为下架）"""
        song = Song.query.get(song_id)
        if not song:
            return False, '歌曲不存在'
        song.status = 0
        db.session.commit()
        return True, None

    @staticmethod
    def get_all_songs(page=1, page_size=10, keyword=None, status=None):
        """管理端获取歌曲列表（含下架）"""
        query = Song.query
        if keyword:
            query = query.filter(Song.title.like(f'%{keyword}%'))
        if status is not None:
            query = query.filter(Song.status == status)
        query = query.order_by(Song.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return [s.to_dict() for s in pagination.items], pagination.total

    # ========= 歌手管理 =========
    @staticmethod
    def create_artist(data):
        """新增歌手"""
        artist = Artist(
            name=data.get('name'),
            avatar=data.get('avatar'),
            region=data.get('region'),
            description=data.get('description'),
        )
        db.session.add(artist)
        db.session.commit()
        return artist

    @staticmethod
    def update_artist(artist_id, data):
        """更新歌手"""
        artist = Artist.query.get(artist_id)
        if not artist:
            return None, '歌手不存在'
        for key in ['name', 'avatar', 'region', 'description']:
            if key in data and data[key] is not None:
                setattr(artist, key, data[key])
        db.session.commit()
        return artist, None

    @staticmethod
    def delete_artist(artist_id):
        """删除歌手"""
        artist = Artist.query.get(artist_id)
        if not artist:
            return False, '歌手不存在'
        if artist.songs.count() > 0:
            return False, '该歌手下有歌曲，无法删除'
        db.session.delete(artist)
        db.session.commit()
        return True, None

    # ========= 流派管理 =========
    @staticmethod
    def create_genre(data):
        """新增流派"""
        if Genre.query.filter_by(name=data.get('name')).first():
            return None, '流派已存在'
        genre = Genre(name=data.get('name'), description=data.get('description'))
        db.session.add(genre)
        db.session.commit()
        return genre

    @staticmethod
    def delete_genre(genre_id):
        """删除流派"""
        genre = Genre.query.get(genre_id)
        if not genre:
            return False, '流派不存在'
        db.session.delete(genre)
        db.session.commit()
        return True, None

    # ========= 评论管理 =========
    @staticmethod
    def get_comments(page=1, page_size=10, status=None):
        """获取评论列表"""
        query = Comment.query
        if status is not None:
            query = query.filter(Comment.status == status)
        query = query.order_by(Comment.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return [c.to_dict() for c in pagination.items], pagination.total

    @staticmethod
    def update_comment_status(comment_id, status):
        """审核评论"""
        comment = Comment.query.get(comment_id)
        if not comment:
            return False, '评论不存在'
        comment.status = status
        db.session.commit()
        return True, None

    # ========= 操作日志 =========
    @staticmethod
    def log_operation(user_id, username, action, module, description='', **kwargs):
        """记录操作日志"""
        log = OperationLog(
            user_id=user_id,
            username=username,
            action=action,
            module=module,
            description=description,
            ip_address=kwargs.get('ip'),
            request_method=kwargs.get('method'),
            request_url=kwargs.get('url'),
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_operation_logs(page=1, page_size=20, module=None):
        """获取操作日志"""
        query = OperationLog.query
        if module:
            query = query.filter(OperationLog.module == module)
        query = query.order_by(OperationLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        return [l.to_dict() for l in pagination.items], pagination.total
