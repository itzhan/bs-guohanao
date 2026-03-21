"""
数据库模型 - 导入汇总
"""
from app.models.user import User
from app.models.song import Song, Artist, Album, Genre
from app.models.interact import Rating, Favorite, Comment, PlayHistory
from app.models.recommend import UserPreference, Recommendation
from app.models.system import OperationLog

__all__ = [
    'User', 'Song', 'Artist', 'Album', 'Genre',
    'Rating', 'Favorite', 'Comment', 'PlayHistory',
    'UserPreference', 'Recommendation', 'OperationLog'
]
