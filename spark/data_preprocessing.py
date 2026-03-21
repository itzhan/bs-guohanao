"""
数据预处理脚本
实现"采集-清洗-特征工程-存储"数据处理流程

功能：
1. 从 MySQL 读取原始音乐数据
2. 数据清洗：去重、缺失值处理、异常值过滤
3. 特征工程：One-Hot 编码流派特征、TF-IDF 提取评论关键词、用户偏好标签生成
4. 输出处理后的数据供 ALS 模型训练使用
"""
import os
import json
from datetime import datetime

import pandas as pd
import numpy as np

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'ab123168'),
    'database': os.getenv('DB_NAME', 'music_recommend'),
}


def load_raw_data():
    """从 MySQL 加载原始数据"""
    import pymysql
    conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')

    songs = pd.read_sql("SELECT * FROM songs WHERE status = 1", conn)
    users = pd.read_sql("SELECT * FROM users WHERE status = 1", conn)
    ratings = pd.read_sql("SELECT * FROM ratings", conn)
    play_history = pd.read_sql("SELECT * FROM play_history", conn)
    favorites = pd.read_sql("SELECT * FROM favorites", conn)
    comments = pd.read_sql("SELECT * FROM comments WHERE status = 1", conn)
    genres = pd.read_sql("SELECT sg.song_id, g.name as genre_name FROM song_genre sg JOIN genres g ON sg.genre_id = g.id", conn)

    conn.close()
    print(f"  原始数据加载完成:")
    print(f"    歌曲: {len(songs)}, 用户: {len(users)}, 评分: {len(ratings)}")
    print(f"    播放记录: {len(play_history)}, 收藏: {len(favorites)}, 评论: {len(comments)}")

    return songs, users, ratings, play_history, favorites, comments, genres


def clean_data(songs, users, ratings, play_history):
    """数据清洗"""
    print("\n[清洗] 执行数据清洗...")

    # 1. 去重
    ratings_before = len(ratings)
    ratings = ratings.drop_duplicates(subset=['user_id', 'song_id'], keep='last')
    print(f"  评分去重: {ratings_before} → {len(ratings)}")

    play_before = len(play_history)
    play_history = play_history.drop_duplicates(subset=['user_id', 'song_id'], keep='last')
    print(f"  播放记录去重: {play_before} → {len(play_history)}")

    # 2. 缺失值处理
    songs['language'] = songs['language'].fillna('未知')
    songs['duration'] = songs['duration'].fillna(songs['duration'].median())
    songs['lyrics'] = songs['lyrics'].fillna('')
    users['age'] = users['age'].fillna(users['age'].median() if not users['age'].isna().all() else 22)
    print(f"  缺失值已填充")

    # 3. 异常值过滤
    # 过滤播放时长 < 1 秒的记录
    invalid_plays = len(play_history[play_history['play_duration'] < 1])
    play_history = play_history[play_history['play_duration'] >= 1]
    print(f"  过滤无效播放记录(时长<1秒): {invalid_plays} 条")

    # 过滤评分不在 1-5 范围的记录
    invalid_ratings = len(ratings[(ratings['score'] < 1) | (ratings['score'] > 5)])
    ratings = ratings[(ratings['score'] >= 1) & (ratings['score'] <= 5)]
    print(f"  过滤无效评分: {invalid_ratings} 条")

    return songs, users, ratings, play_history


def feature_engineering(songs, genres, comments):
    """特征工程"""
    print("\n[特征] 执行特征工程...")

    # 1. One-Hot 编码流派特征
    genre_pivot = genres.pivot_table(
        index='song_id',
        columns='genre_name',
        aggfunc='size',
        fill_value=0
    ).reset_index()
    songs = songs.merge(genre_pivot, left_on='id', right_on='song_id', how='left')
    print(f"  流派 One-Hot 编码: {len(genre_pivot.columns) - 1} 个流派")

    # 2. TF-IDF 提取评论关键词
    if len(comments) > 0:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            # 按歌曲聚合评论
            song_comments = comments.groupby('song_id')['content'].apply(' '.join).reset_index()
            vectorizer = TfidfVectorizer(max_features=50)
            tfidf_matrix = vectorizer.fit_transform(song_comments['content'])
            feature_names = vectorizer.get_feature_names_out()
            print(f"  TF-IDF 关键词提取: {len(feature_names)} 个特征词")
            print(f"    Top 10 关键词: {', '.join(feature_names[:10])}")
        except Exception as e:
            print(f"  TF-IDF 提取跳过: {e}")

    # 3. 数据统计
    print(f"\n[统计] 处理后数据概况:")
    print(f"  歌曲数: {len(songs)}")
    print(f"  语言分布: {dict(songs['language'].value_counts())}")
    print(f"  平均评分: {songs['avg_rating'].mean():.2f}")
    print(f"  平均播放次数: {songs['play_count'].mean():.0f}")

    return songs


def generate_user_tags(users, ratings, genres):
    """基于用户行为生成偏好标签"""
    print("\n[标签] 生成用户偏好标签...")

    if ratings.empty:
        return users

    # 用户评分 >= 4 的歌曲的流派
    high_ratings = ratings[ratings['score'] >= 4]
    if high_ratings.empty:
        return users

    user_genre = high_ratings.merge(genres, on='song_id')
    user_genre_counts = user_genre.groupby(['user_id', 'genre_name']).size().reset_index(name='count')

    # 每个用户取 Top 3 流派
    top_genres = user_genre_counts.sort_values(['user_id', 'count'], ascending=[True, False]) \
        .groupby('user_id').head(3)

    user_tags = top_genres.groupby('user_id')['genre_name'].apply(list).reset_index()
    user_tags.columns = ['id', 'generated_tags']
    user_tags['generated_tags'] = user_tags['generated_tags'].apply(json.dumps, ensure_ascii=False)

    users = users.merge(user_tags, left_on='id', right_on='id', how='left')
    tagged_count = users['generated_tags'].notna().sum()
    print(f"  已为 {tagged_count} 个用户生成偏好标签")

    return users


def main():
    print("=" * 60)
    print("  音乐推荐系统 - 数据预处理脚本")
    print("=" * 60)
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 加载原始数据
    print("\n[1/4] 加载原始数据...")
    songs, users, ratings, play_history, favorites, comments, genres = load_raw_data()

    # 2. 数据清洗
    songs, users, ratings, play_history = clean_data(songs, users, ratings, play_history)

    # 3. 特征工程
    songs = feature_engineering(songs, genres, comments)

    # 4. 用户标签生成
    users = generate_user_tags(users, ratings, genres)

    # 输出结果到 CSV（供其他脚本使用）
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)

    songs.to_csv(os.path.join(output_dir, 'processed_songs.csv'), index=False, encoding='utf-8-sig')
    users.to_csv(os.path.join(output_dir, 'processed_users.csv'), index=False, encoding='utf-8-sig')
    ratings.to_csv(os.path.join(output_dir, 'processed_ratings.csv'), index=False, encoding='utf-8-sig')
    play_history.to_csv(os.path.join(output_dir, 'processed_play_history.csv'), index=False, encoding='utf-8-sig')

    print(f"\n  处理结果已保存到 {output_dir}/")
    print(f"  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
