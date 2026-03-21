"""
用户互动服务：评分、收藏、评论、播放记录
"""
from datetime import datetime
from app.extensions import db
from app.models.interact import Rating, Favorite, Comment, PlayHistory
from app.models.song import Song


class InteractService:

    # ========= 评分 =========
    @staticmethod
    def rate_song(user_id, song_id, score):
        """给歌曲评分（1-5分，可更新）"""
        if score < 1 or score > 5:
            return None, '评分必须在1-5之间'

        song = Song.query.get(song_id)
        if not song:
            return None, '歌曲不存在'

        rating = Rating.query.filter_by(user_id=user_id, song_id=song_id).first()
        if rating:
            rating.score = score
            rating.updated_at = datetime.now()
        else:
            rating = Rating(user_id=user_id, song_id=song_id, score=score)
            db.session.add(rating)

        # 更新歌曲平均评分
        db.session.flush()
        avg = db.session.query(db.func.avg(Rating.score)).filter(Rating.song_id == song_id).scalar()
        count = Rating.query.filter_by(song_id=song_id).count()
        song.avg_rating = round(float(avg), 1) if avg else 0
        song.rating_count = count

        db.session.commit()
        return rating, None

    @staticmethod
    def get_user_rating(user_id, song_id):
        """获取用户对某歌曲的评分"""
        return Rating.query.filter_by(user_id=user_id, song_id=song_id).first()

    # ========= 收藏 =========
    @staticmethod
    def toggle_favorite(user_id, song_id):
        """收藏/取消收藏"""
        song = Song.query.get(song_id)
        if not song:
            return False, '歌曲不存在', False

        fav = Favorite.query.filter_by(user_id=user_id, song_id=song_id).first()
        if fav:
            db.session.delete(fav)
            song.favorite_count = max(0, song.favorite_count - 1)
            db.session.commit()
            return True, '取消收藏成功', False
        else:
            fav = Favorite(user_id=user_id, song_id=song_id)
            db.session.add(fav)
            song.favorite_count += 1
            db.session.commit()
            return True, '收藏成功', True

    @staticmethod
    def get_user_favorites(user_id, page=1, page_size=10):
        """获取用户收藏列表"""
        query = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [f.to_dict() for f in pagination.items]
        return items, pagination.total

    @staticmethod
    def is_favorited(user_id, song_id):
        """检查是否已收藏"""
        return Favorite.query.filter_by(user_id=user_id, song_id=song_id).first() is not None

    # ========= 评论 =========
    @staticmethod
    def add_comment(user_id, song_id, content, parent_id=None):
        """添加评论"""
        song = Song.query.get(song_id)
        if not song:
            return None, '歌曲不存在'

        comment = Comment(
            user_id=user_id,
            song_id=song_id,
            content=content,
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()
        return comment, None

    @staticmethod
    def get_song_comments(song_id, page=1, page_size=20):
        """获取歌曲评论列表（仅顶层）"""
        query = Comment.query.filter_by(song_id=song_id, parent_id=None, status=1) \
            .order_by(Comment.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [c.to_dict() for c in pagination.items]
        return items, pagination.total

    @staticmethod
    def delete_comment(comment_id, user_id):
        """删除评论（仅本人或管理员）"""
        comment = Comment.query.get(comment_id)
        if not comment:
            return False, '评论不存在'
        if comment.user_id != user_id:
            return False, '无权删除该评论'
        comment.status = 0
        db.session.commit()
        return True, None

    # ========= 播放记录 =========
    @staticmethod
    def record_play(user_id, song_id, duration=0):
        """记录播放"""
        song = Song.query.get(song_id)
        if not song:
            return None, '歌曲不存在'

        # 更新歌曲播放次数
        song.play_count += 1

        # 更新用户播放记录
        history = PlayHistory.query.filter_by(user_id=user_id, song_id=song_id).first()
        if history:
            history.play_count += 1
            history.play_duration += duration
            history.updated_at = datetime.now()
        else:
            history = PlayHistory(user_id=user_id, song_id=song_id, play_duration=duration)
            db.session.add(history)

        db.session.commit()

        # 记录到 MongoDB 行为日志
        _log_behavior(user_id, song_id, 'play', duration)

        return history, None

    @staticmethod
    def get_user_history(user_id, page=1, page_size=20):
        """获取用户播放历史"""
        query = PlayHistory.query.filter_by(user_id=user_id).order_by(PlayHistory.updated_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [h.to_dict() for h in pagination.items]
        return items, pagination.total


def _log_behavior(user_id, song_id, action, duration=0):
    """记录用户行为到 MongoDB（非阻塞，失败不影响主流程）"""
    try:
        from app.extensions import mongo
        if mongo.db is not None:
            mongo.get_collection('user_behaviors').insert_one({
                'user_id': user_id,
                'song_id': song_id,
                'action': action,
                'duration': duration,
                'timestamp': datetime.now()
            })
    except Exception:
        pass  # MongoDB 不可用时静默忽略
