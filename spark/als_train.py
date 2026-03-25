"""
PySpark ALS 推荐模型训练脚本
基于 Spark MLlib 的交替最小二乘法（ALS）实现个性化音乐推荐

使用方式（本地模式）：
    python als_train.py

算法说明：
    ALS (Alternating Least Squares) 是一种矩阵分解技术，通过将用户-物品交互矩阵
    分解为两个低秩矩阵（用户特征矩阵和物品特征矩阵），来预测用户对未接触物品的偏好。
    
    优化措施：
    - 引入时间衰减因子：近期行为权重更高
    - 冷启动处理：新用户通过偏好问卷生成初始推荐
    - 隐式反馈：结合播放时长、收藏、评分等多维度行为
"""
import os
import sys
import json
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

# 尝试导入 PySpark（如不可用则使用 scikit-learn 替代）
try:
    from pyspark.sql import SparkSession
    from pyspark.ml.recommendation import ALS
    from pyspark.ml.evaluation import RegressionEvaluator
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    print("[INFO] PySpark 未安装，将使用 scikit-learn 的 NMF 替代方案")

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'ab123168'),
    'database': os.getenv('DB_NAME', 'music_recommend'),
}

# HDFS 配置
HDFS_HOST = os.getenv('HDFS_HOST', 'namenode')
HDFS_PORT = int(os.getenv('HDFS_PORT', 9000))
HDFS_BASE_PATH = '/music/processed'


def load_data_from_hdfs():
    """尝试从 HDFS 加载预处理后的数据"""
    try:
        from hdfs import InsecureClient
        hdfs_url = os.getenv('HDFS_URL', f'http://{HDFS_HOST}:9870')
        client = InsecureClient(hdfs_url, user='root')

        # 检查 HDFS 上是否有预处理数据
        status = client.status(HDFS_BASE_PATH, strict=False)
        if status is None:
            print("  HDFS 上无预处理数据，回退到 MySQL")
            return None, None, None

        print(f"  从 HDFS ({HDFS_BASE_PATH}) 读取预处理数据...")
        import io

        with client.read(f'{HDFS_BASE_PATH}/processed_ratings.csv') as reader:
            ratings_df = pd.read_csv(io.BytesIO(reader.read()))
        with client.read(f'{HDFS_BASE_PATH}/processed_play_history.csv') as reader:
            play_df = pd.read_csv(io.BytesIO(reader.read()))

        # 收藏数据需要从 MySQL 获取（预处理脚本未导出）
        import pymysql
        conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')
        fav_df = pd.read_sql("SELECT user_id, song_id, created_at FROM favorites", conn)
        conn.close()

        print(f"  ✓ 从 HDFS 成功加载数据")
        return ratings_df, play_df, fav_df

    except ImportError:
        print("  hdfs 库未安装，回退到 MySQL")
        return None, None, None
    except Exception as e:
        print(f"  HDFS 读取失败 ({e})，回退到 MySQL")
        return None, None, None


def load_data_with_hdfs_fallback():
    """优先从 HDFS 加载数据，失败则从 MySQL 加载"""
    ratings_df, play_df, fav_df = load_data_from_hdfs()
    if ratings_df is not None:
        return ratings_df, play_df, fav_df
    print("  从 MySQL 直接加载数据...")
    return load_data_from_mysql()


def load_data_from_mysql():
    """从 MySQL 加载用户行为数据"""
    import pymysql

    conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')

    # 加载评分数据
    ratings_df = pd.read_sql(
        "SELECT user_id, song_id, score, created_at FROM ratings", conn
    )

    # 加载播放记录（转化为隐式评分）
    play_df = pd.read_sql(
        "SELECT user_id, song_id, play_count, play_duration, updated_at FROM play_history", conn
    )

    # 加载收藏数据
    fav_df = pd.read_sql(
        "SELECT user_id, song_id, created_at FROM favorites", conn
    )

    conn.close()
    return ratings_df, play_df, fav_df


def compute_interaction_scores(ratings_df, play_df, fav_df):
    """
    计算综合交互分数
    
    权重策略：
    - 显式评分：直接使用 (1-5分)
    - 播放行为：归一化后 * 0.6 + 播放时长归一化 * 0.4，再映射到 1-5
    - 收藏行为：固定加 0.5 分
    - 时间衰减：weight = score * (0.9)^((now - action_time) / 30天)
    """
    now = datetime.now()

    # 1. 处理显式评分
    if not ratings_df.empty:
        ratings_df['time_decay'] = ratings_df['created_at'].apply(
            lambda t: 0.9 ** ((now - t).days / 30) if pd.notna(t) else 1.0
        )
        ratings_df['weighted_score'] = ratings_df['score'] * ratings_df['time_decay']
        scores = ratings_df[['user_id', 'song_id', 'weighted_score']].copy()
        scores.columns = ['user_id', 'song_id', 'score']
    else:
        scores = pd.DataFrame(columns=['user_id', 'song_id', 'score'])

    # 2. 处理播放行为 → 隐式评分
    if not play_df.empty:
        max_play = play_df['play_count'].max()
        max_dur = play_df['play_duration'].max()
        if max_play > 0 and max_dur > 0:
            play_df['norm_count'] = play_df['play_count'] / max_play
            play_df['norm_dur'] = play_df['play_duration'] / max_dur
            play_df['implicit_score'] = (play_df['norm_count'] * 0.6 + play_df['norm_dur'] * 0.4) * 4 + 1
            play_df['time_decay'] = play_df['updated_at'].apply(
                lambda t: 0.9 ** ((now - t).days / 30) if pd.notna(t) else 1.0
            )
            play_df['weighted_score'] = play_df['implicit_score'] * play_df['time_decay']
            play_scores = play_df[['user_id', 'song_id', 'weighted_score']].copy()
            play_scores.columns = ['user_id', 'song_id', 'score']
            scores = pd.concat([scores, play_scores], ignore_index=True)

    # 3. 处理收藏 → 加分
    if not fav_df.empty:
        fav_scores = fav_df[['user_id', 'song_id']].copy()
        fav_scores['score'] = 0.5
        scores = pd.concat([scores, fav_scores], ignore_index=True)

    # 4. 合并同一 user-song 的所有评分
    final_scores = scores.groupby(['user_id', 'song_id']).agg({'score': 'sum'}).reset_index()
    final_scores['score'] = final_scores['score'].clip(1.0, 5.0)  # 限制在 1-5 范围

    return final_scores


def train_with_spark(interaction_df):
    """使用 PySpark ALS 训练推荐模型"""
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("MusicRecommendALS") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 转换为 Spark DataFrame
    spark_df = spark.createDataFrame(interaction_df[['user_id', 'song_id', 'score']])

    # 拆分训练集和测试集
    train, test = spark_df.randomSplit([0.8, 0.2], seed=42)

    # 构建 ALS 模型
    als = ALS(
        maxIter=15,
        regParam=0.1,
        rank=20,
        userCol="user_id",
        itemCol="song_id",
        ratingCol="score",
        coldStartStrategy="drop",
        nonnegative=True,
        seed=42
    )

    model = als.fit(train)

    # 评估
    predictions = model.transform(test)
    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="score",
        predictionCol="prediction"
    )
    rmse = evaluator.evaluate(predictions)
    print(f"[ALS] 测试集 RMSE = {rmse:.4f}")

    # 为每个用户生成 Top-20 推荐
    user_recs = model.recommendForAllUsers(20)
    recs_list = []
    for row in user_recs.collect():
        user_id = row['user_id']
        for rec in row['recommendations']:
            recs_list.append({
                'user_id': user_id,
                'song_id': rec['song_id'],
                'score': round(float(rec['rating']), 4),
            })

    spark.stop()
    return pd.DataFrame(recs_list)


def train_with_sklearn(interaction_df):
    """使用 scikit-learn NMF 替代方案（无需 Spark）"""
    from sklearn.decomposition import NMF

    # 构建用户-歌曲矩阵
    user_ids = interaction_df['user_id'].unique()
    song_ids = interaction_df['song_id'].unique()
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    song_map = {sid: i for i, sid in enumerate(song_ids)}

    matrix = np.zeros((len(user_ids), len(song_ids)))
    for _, row in interaction_df.iterrows():
        matrix[user_map[row['user_id']], song_map[row['song_id']]] = row['score']

    # NMF 矩阵分解
    model = NMF(n_components=20, init='random', random_state=42, max_iter=200)
    W = model.fit_transform(matrix)  # 用户特征矩阵
    H = model.components_  # 物品特征矩阵

    # 重建评分矩阵
    predicted = W @ H

    # 为每个用户取 Top-20 未交互歌曲
    recs_list = []
    reverse_song_map = {v: k for k, v in song_map.items()}

    for uid, u_idx in user_map.items():
        user_scores = predicted[u_idx]
        # 已交互的歌曲
        known = set(interaction_df[interaction_df['user_id'] == uid]['song_id'].tolist())

        candidates = []
        for s_idx, score in enumerate(user_scores):
            real_sid = reverse_song_map[s_idx]
            if real_sid not in known:
                candidates.append((real_sid, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        for song_id, score in candidates[:20]:
            recs_list.append({
                'user_id': uid,
                'song_id': song_id,
                'score': round(float(score), 4),
            })

    reconstruction_error = model.reconstruction_err_
    print(f"[NMF] 重建误差 = {reconstruction_error:.4f}")

    return pd.DataFrame(recs_list)


def save_recommendations(recs_df):
    """将推荐结果保存到 MySQL"""
    import pymysql

    conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')
    cursor = conn.cursor()

    # 清空旧推荐（保留其他算法的结果）
    cursor.execute("DELETE FROM recommendations WHERE algorithm = 'ALS'")

    # 获取歌曲标题用于生成推荐理由
    cursor.execute("SELECT id, title FROM songs")
    song_titles = dict(cursor.fetchall())

    # 批量插入
    insert_sql = """
        INSERT INTO recommendations (user_id, song_id, score, algorithm, reason, is_read, created_at)
        VALUES (%s, %s, %s, 'ALS', %s, 0, NOW())
        ON DUPLICATE KEY UPDATE score = VALUES(score), reason = VALUES(reason), created_at = NOW()
    """

    count = 0
    for _, row in recs_df.iterrows():
        song_title = song_titles.get(row['song_id'], '未知歌曲')
        reason = f'基于您的听歌偏好，为您推荐《{song_title}》'
        try:
            cursor.execute(insert_sql, (row['user_id'], row['song_id'], row['score'], reason))
            count += 1
        except Exception as e:
            pass  # 跳过外键错误（如用户/歌曲不存在）

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[保存] 成功写入 {count} 条推荐结果到数据库")


def main():
    print("=" * 60)
    print("  基于大数据的音乐推荐与数据分析系统 - ALS 推荐模型训练")
    print("=" * 60)
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 加载数据（优先从 HDFS 读取预处理数据，失败则回退 MySQL）
    print("[1/4] 加载用户行为数据...")
    ratings_df, play_df, fav_df = load_data_with_hdfs_fallback()
    print(f"  评分记录: {len(ratings_df)} 条")
    print(f"  播放记录: {len(play_df)} 条")
    print(f"  收藏记录: {len(fav_df)} 条")

    # 2. 计算交互分数
    print("\n[2/4] 计算综合交互分数（含时间衰减）...")
    interaction_df = compute_interaction_scores(ratings_df, play_df, fav_df)
    print(f"  综合交互记录: {len(interaction_df)} 条")
    print(f"  用户数: {interaction_df['user_id'].nunique()}")
    print(f"  歌曲数: {interaction_df['song_id'].nunique()}")

    # 3. 训练模型
    print("\n[3/4] 训练推荐模型...")
    if SPARK_AVAILABLE:
        print("  使用 PySpark ALS 算法")
        recs_df = train_with_spark(interaction_df)
    else:
        print("  使用 scikit-learn NMF 替代算法")
        recs_df = train_with_sklearn(interaction_df)

    print(f"  生成推荐结果: {len(recs_df)} 条")

    # 4. 保存结果
    print("\n[4/4] 保存推荐结果到数据库...")
    save_recommendations(recs_df)

    print(f"\n  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
