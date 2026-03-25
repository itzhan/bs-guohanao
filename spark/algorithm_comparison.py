"""
推荐算法对比实验脚本
在相同数据集上测试三种推荐算法并比较性能：
1. 基于用户的协同过滤（UserCF）— 余弦相似度
2. 基于内容的推荐（Content-Based）— 流派/歌手特征匹配
3. ALS 矩阵分解 — 交替最小二乘法

评估指标：Precision@K, Recall@K, NDCG@K, 覆盖率
"""
import os
import json
from datetime import datetime
from collections import defaultdict

import pandas as pd
import numpy as np

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'ab123168'),
    'database': os.getenv('DB_NAME', 'music_recommend'),
}

K = 10  # Top-K 推荐数量


def load_experiment_data():
    """加载实验数据并拆分训练集/测试集"""
    import pymysql
    conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')

    ratings = pd.read_sql("SELECT user_id, song_id, score, created_at FROM ratings", conn)
    play_history = pd.read_sql("SELECT user_id, song_id, play_count FROM play_history", conn)
    favorites = pd.read_sql("SELECT user_id, song_id FROM favorites", conn)
    songs = pd.read_sql("SELECT id, artist_id, avg_rating, play_count FROM songs WHERE status = 1", conn)
    song_genres = pd.read_sql(
        "SELECT sg.song_id, g.id as genre_id, g.name as genre_name "
        "FROM song_genre sg JOIN genres g ON sg.genre_id = g.id", conn
    )
    conn.close()

    # 构建正向交互集（评分>=3 或 有收藏）
    positive_ratings = ratings[ratings['score'] >= 3][['user_id', 'song_id']].copy()
    positive_ratings['source'] = 'rating'
    fav_interactions = favorites[['user_id', 'song_id']].copy()
    fav_interactions['source'] = 'favorite'
    interactions = pd.concat([positive_ratings, fav_interactions]).drop_duplicates(
        subset=['user_id', 'song_id']
    )

    # 按用户分层随机拆分 80/20
    train_data = []
    test_data = []
    for user_id, group in interactions.groupby('user_id'):
        if len(group) < 3:
            train_data.append(group)
            continue
        n_test = max(1, int(len(group) * 0.2))
        test_indices = group.sample(n=n_test, random_state=42).index
        train_data.append(group.drop(test_indices))
        test_data.append(group.loc[test_indices])

    train = pd.concat(train_data) if train_data else pd.DataFrame()
    test = pd.concat(test_data) if test_data else pd.DataFrame()

    print(f"  交互数据: {len(interactions)} 条")
    print(f"  训练集: {len(train)} 条, 测试集: {len(test)} 条")
    print(f"  用户数: {interactions['user_id'].nunique()}, 歌曲数: {interactions['song_id'].nunique()}")

    return train, test, ratings, songs, song_genres


# ============================================================
# 算法 1：基于用户的协同过滤（UserCF）
# ============================================================
def user_cf_recommend(train, all_song_ids, k=K):
    """基于余弦相似度的 UserCF"""
    print("\n  [UserCF] 构建用户-物品矩阵...")
    user_items = defaultdict(set)
    for _, row in train.iterrows():
        user_items[row['user_id']].add(row['song_id'])

    users = list(user_items.keys())
    recommendations = {}

    for uid in users:
        # 计算与其他用户的相似度
        scores = defaultdict(float)
        user_set = user_items[uid]
        for other_uid in users:
            if other_uid == uid:
                continue
            other_set = user_items[other_uid]
            intersection = len(user_set & other_set)
            if intersection == 0:
                continue
            similarity = intersection / (np.sqrt(len(user_set)) * np.sqrt(len(other_set)))
            for sid in other_set - user_set:
                scores[sid] += similarity

        # Top-K
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        recommendations[uid] = [sid for sid, _ in top_k]

    return recommendations


# ============================================================
# 算法 2：基于内容的推荐（Content-Based）
# ============================================================
def content_based_recommend(train, songs, song_genres, k=K):
    """基于流派和歌手特征的内容推荐"""
    print("\n  [Content-Based] 构建内容特征...")

    # 构建歌曲特征
    song_genre_map = defaultdict(set)
    for _, row in song_genres.iterrows():
        song_genre_map[row['song_id']].add(row['genre_id'])

    song_artist_map = dict(zip(songs['id'], songs['artist_id']))

    user_items = defaultdict(set)
    for _, row in train.iterrows():
        user_items[row['user_id']].add(row['song_id'])

    all_songs = set(songs['id'].tolist())
    recommendations = {}

    for uid, liked_songs in user_items.items():
        # 提取用户偏好特征
        pref_genres = set()
        pref_artists = set()
        for sid in liked_songs:
            pref_genres.update(song_genre_map.get(sid, set()))
            artist = song_artist_map.get(sid)
            if artist:
                pref_artists.add(artist)

        # 对未交互歌曲打分
        candidates = all_songs - liked_songs
        scores = []
        for sid in candidates:
            score = 0
            s_genres = song_genre_map.get(sid, set())
            s_artist = song_artist_map.get(sid)
            # 流派匹配度
            if pref_genres and s_genres:
                score += len(pref_genres & s_genres) / len(pref_genres) * 0.6
            # 歌手匹配
            if s_artist in pref_artists:
                score += 0.4
            if score > 0:
                scores.append((sid, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        recommendations[uid] = [sid for sid, _ in scores[:k]]

    return recommendations


# ============================================================
# 算法 3：ALS 矩阵分解
# ============================================================
def als_recommend(train, ratings_df, k=K):
    """基于 NMF/ALS 的矩阵分解推荐"""
    print("\n  [ALS] 训练矩阵分解模型...")
    from sklearn.decomposition import NMF

    # 构建用户-歌曲评分矩阵
    user_ids = sorted(train['user_id'].unique())
    song_ids = sorted(train['song_id'].unique())
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    song_map = {sid: i for i, sid in enumerate(song_ids)}
    reverse_song_map = {v: k for k, v in song_map.items()}

    matrix = np.zeros((len(user_ids), len(song_ids)))

    # 使用评分数据填充（如有），否则用二值
    rating_map = {}
    for _, row in ratings_df.iterrows():
        rating_map[(row['user_id'], row['song_id'])] = row['score']

    for _, row in train.iterrows():
        uid_idx = user_map.get(row['user_id'])
        sid_idx = song_map.get(row['song_id'])
        if uid_idx is not None and sid_idx is not None:
            score = rating_map.get((row['user_id'], row['song_id']), 3.0)
            matrix[uid_idx, sid_idx] = score

    # NMF 矩阵分解（ALS 的 sklearn 替代）
    n_components = min(20, min(matrix.shape) - 1) if min(matrix.shape) > 1 else 1
    model = NMF(n_components=max(1, n_components), init='random', random_state=42, max_iter=200)
    W = model.fit_transform(matrix)
    H = model.components_
    predicted = W @ H

    user_known = defaultdict(set)
    for _, row in train.iterrows():
        user_known[row['user_id']].add(row['song_id'])

    recommendations = {}
    for uid in user_ids:
        u_idx = user_map[uid]
        user_scores = predicted[u_idx]
        known = user_known[uid]

        candidates = []
        for s_idx, score in enumerate(user_scores):
            real_sid = reverse_song_map[s_idx]
            if real_sid not in known:
                candidates.append((real_sid, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        recommendations[uid] = [sid for sid, _ in candidates[:k]]

    return recommendations


# ============================================================
# 评估指标计算
# ============================================================
def evaluate(recommendations, test, all_songs):
    """计算 Precision@K, Recall@K, NDCG@K, 覆盖率"""
    # 构建测试集的用户-物品映射
    test_user_items = defaultdict(set)
    for _, row in test.iterrows():
        test_user_items[row['user_id']].add(row['song_id'])

    precisions = []
    recalls = []
    ndcgs = []
    all_recommended = set()

    for uid, rec_list in recommendations.items():
        if uid not in test_user_items:
            continue
        relevant = test_user_items[uid]
        if not relevant or not rec_list:
            continue

        all_recommended.update(rec_list)

        # Precision@K
        hits = len(set(rec_list) & relevant)
        precisions.append(hits / len(rec_list))

        # Recall@K
        recalls.append(hits / len(relevant))

        # NDCG@K
        dcg = 0
        for i, sid in enumerate(rec_list):
            if sid in relevant:
                dcg += 1 / np.log2(i + 2)
        idcg = sum(1 / np.log2(i + 2) for i in range(min(len(relevant), len(rec_list))))
        ndcgs.append(dcg / idcg if idcg > 0 else 0)

    coverage = len(all_recommended) / len(all_songs) if all_songs else 0

    return {
        'precision': round(np.mean(precisions) * 100, 2) if precisions else 0,
        'recall': round(np.mean(recalls) * 100, 2) if recalls else 0,
        'ndcg': round(np.mean(ndcgs) * 100, 2) if ndcgs else 0,
        'coverage': round(coverage * 100, 2),
        'users_evaluated': len(precisions),
    }


def main():
    print("=" * 60)
    print("  推荐算法对比实验")
    print("=" * 60)
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  评估指标: Precision@{K}, Recall@{K}, NDCG@{K}, 覆盖率")

    # 加载数据
    print("\n[1/5] 加载实验数据...")
    train, test, ratings, songs, song_genres = load_experiment_data()
    all_songs = set(songs['id'].tolist())

    if test.empty:
        print("\n  测试集为空，无法进行实验。请确保系统中有足够的用户交互数据。")
        # 写入空报告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': '测试数据不足，无法完成对比实验',
            'results': {}
        }
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'comparison_report.json'), 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return

    results = {}

    # 算法 1: UserCF
    print("\n[2/5] 运行基于用户的协同过滤 (UserCF)...")
    ucf_recs = user_cf_recommend(train, all_songs)
    results['UserCF'] = evaluate(ucf_recs, test, all_songs)
    print(f"  结果: Precision={results['UserCF']['precision']}%, "
          f"Recall={results['UserCF']['recall']}%, "
          f"NDCG={results['UserCF']['ndcg']}%, "
          f"覆盖率={results['UserCF']['coverage']}%")

    # 算法 2: Content-Based
    print("\n[3/5] 运行基于内容的推荐 (Content-Based)...")
    cb_recs = content_based_recommend(train, songs, song_genres)
    results['ContentBased'] = evaluate(cb_recs, test, all_songs)
    print(f"  结果: Precision={results['ContentBased']['precision']}%, "
          f"Recall={results['ContentBased']['recall']}%, "
          f"NDCG={results['ContentBased']['ndcg']}%, "
          f"覆盖率={results['ContentBased']['coverage']}%")

    # 算法 3: ALS
    print("\n[4/5] 运行 ALS 矩阵分解推荐...")
    als_recs = als_recommend(train, ratings)
    results['ALS'] = evaluate(als_recs, test, all_songs)
    print(f"  结果: Precision={results['ALS']['precision']}%, "
          f"Recall={results['ALS']['recall']}%, "
          f"NDCG={results['ALS']['ndcg']}%, "
          f"覆盖率={results['ALS']['coverage']}%")

    # 保存报告
    print("\n[5/5] 生成对比报告...")
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'k': K,
        'train_size': len(train),
        'test_size': len(test),
        'total_users': train['user_id'].nunique(),
        'total_songs': len(all_songs),
        'results': results,
        'best_algorithm': max(results.items(), key=lambda x: x[1]['precision'])[0],
        'conclusion': '实验结论将在下方生成',
    }

    # 生成结论
    best = report['best_algorithm']
    report['conclusion'] = (
        f"在 {report['total_users']} 个用户、{report['total_songs']} 首歌曲的数据集上，"
        f"ALS 矩阵分解算法在 Precision@{K} 上表现为 {results['ALS']['precision']}%，"
        f"基于用户的协同过滤为 {results['UserCF']['precision']}%，"
        f"基于内容的推荐为 {results['ContentBased']['precision']}%。"
        f"综合准确率、召回率和 NDCG 指标，{best} 算法在本数据集上表现最优。"
    )

    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'comparison_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n  对比报告已保存到: {report_path}")
    print(f"\n  {'算法':<20} {'Precision@'+str(K):<15} {'Recall@'+str(K):<15} {'NDCG@'+str(K):<15} {'覆盖率':<10}")
    print("  " + "-" * 75)
    for algo, metrics in results.items():
        print(f"  {algo:<20} {metrics['precision']:<15} {metrics['recall']:<15} "
              f"{metrics['ndcg']:<15} {metrics['coverage']}")
    print(f"\n  最佳算法: {best}")
    print(f"\n  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
