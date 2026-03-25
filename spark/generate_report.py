"""
Matplotlib 离线分析报告生成脚本
生成 PNG 图表组合报告，覆盖：
1. 评分分布直方图
2. 流派占比饼图
3. 播放趋势折线图
4. 用户活跃度热力图
5. 算法对比结果（如已运行过 algorithm_comparison.py）
"""
import os
import json
from datetime import datetime

import pandas as pd
import numpy as np

# 设置 Matplotlib 中文支持
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt

# 尝试使用中文字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'ab123168'),
    'database': os.getenv('DB_NAME', 'music_recommend'),
}


def load_data():
    """加载分析所需数据"""
    import pymysql
    conn = pymysql.connect(**DB_CONFIG, charset='utf8mb4')

    ratings = pd.read_sql("SELECT score FROM ratings", conn)
    song_genres = pd.read_sql(
        "SELECT g.name FROM song_genre sg JOIN genres g ON sg.genre_id = g.id", conn
    )
    play_history = pd.read_sql(
        "SELECT created_at, user_id FROM play_history WHERE created_at IS NOT NULL",
        conn, parse_dates=['created_at']
    )
    users = pd.read_sql("SELECT gender, age FROM users WHERE status = 1", conn)
    songs = pd.read_sql("SELECT language, play_count, avg_rating FROM songs WHERE status = 1", conn)

    conn.close()
    return ratings, song_genres, play_history, users, songs


def plot_rating_distribution(ax, ratings):
    """评分分布直方图"""
    counts = ratings['score'].value_counts().sort_index()
    colors = ['#FF6B6B', '#FFA94D', '#FFD43B', '#69DB7C', '#4DABF7']
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], edgecolor='white', width=0.7)
    ax.set_title('Rating Distribution', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Rating Score')
    ax.set_ylabel('Count')
    ax.set_xticks([1, 2, 3, 4, 5])
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_genre_distribution(ax, song_genres):
    """流派占比饼图"""
    genre_counts = song_genres['name'].value_counts().head(8)
    colors = plt.cm.Set3(np.linspace(0, 1, len(genre_counts)))
    wedges, texts, autotexts = ax.pie(
        genre_counts.values, labels=genre_counts.index,
        autopct='%1.1f%%', colors=colors, startangle=140,
        pctdistance=0.85
    )
    for text in autotexts:
        text.set_fontsize(9)
    ax.set_title('Genre Distribution', fontsize=14, fontweight='bold', pad=10)


def plot_play_trend(ax, play_history):
    """播放趋势折线图（近30天）"""
    if play_history.empty:
        ax.text(0.5, 0.5, 'No play data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Play Trend (30 Days)', fontsize=14, fontweight='bold', pad=10)
        return

    play_history['date'] = play_history['created_at'].dt.date
    daily = play_history.groupby('date').size().reset_index(name='count')
    daily = daily.sort_values('date').tail(30)

    ax.fill_between(range(len(daily)), daily['count'], alpha=0.3, color='#4DABF7')
    ax.plot(range(len(daily)), daily['count'], color='#4DABF7', linewidth=2, marker='o', markersize=4)
    ax.set_title('Play Trend (30 Days)', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Date')
    ax.set_ylabel('Plays')

    # 只显示部分日期标签
    tick_indices = list(range(0, len(daily), max(1, len(daily) // 6)))
    ax.set_xticks(tick_indices)
    ax.set_xticklabels([str(daily.iloc[i]['date'])[5:] for i in tick_indices], rotation=45, fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_user_activity(ax, play_history):
    """用户活跃时段分布"""
    if play_history.empty:
        ax.text(0.5, 0.5, 'No activity data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('User Activity by Hour', fontsize=14, fontweight='bold', pad=10)
        return

    hours = play_history['created_at'].dt.hour
    hour_counts = hours.value_counts().sort_index()
    all_hours = range(24)
    counts = [hour_counts.get(h, 0) for h in all_hours]

    colors = ['#FF6B6B' if c > np.percentile(counts, 75) else '#4DABF7' for c in counts]
    ax.bar(all_hours, counts, color=colors, edgecolor='white', width=0.8)
    ax.set_title('User Activity by Hour', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Hour (0-23)')
    ax.set_ylabel('Play Count')
    ax.set_xticks(range(0, 24, 2))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_language_distribution(ax, songs):
    """语言分布柱状图"""
    lang_counts = songs['language'].value_counts().head(6)
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(lang_counts)))
    bars = ax.barh(lang_counts.index, lang_counts.values, color=colors, edgecolor='white', height=0.6)
    ax.set_title('Language Distribution', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Song Count')
    for bar, val in zip(bars, lang_counts.values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(val), ha='left', va='center', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()


def plot_algorithm_comparison(ax, output_dir):
    """算法对比结果（从 comparison_report.json 读取）"""
    report_path = os.path.join(output_dir, 'comparison_report.json')
    if not os.path.exists(report_path):
        ax.text(0.5, 0.5, 'No comparison data\n(Run algorithm_comparison.py first)',
                ha='center', va='center', transform=ax.transAxes, fontsize=11)
        ax.set_title('Algorithm Comparison', fontsize=14, fontweight='bold', pad=10)
        return

    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    if 'error' in report:
        ax.text(0.5, 0.5, report['error'], ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Algorithm Comparison', fontsize=14, fontweight='bold', pad=10)
        return

    results = report['results']
    algos = list(results.keys())
    metrics = ['precision', 'recall', 'ndcg']
    x = np.arange(len(algos))
    width = 0.25
    colors = ['#4DABF7', '#69DB7C', '#FFA94D']

    for i, metric in enumerate(metrics):
        values = [results[algo][metric] for algo in algos]
        bars = ax.bar(x + i * width, values, width, label=f'{metric.upper()}@K', color=colors[i], edgecolor='white')

    ax.set_title('Algorithm Comparison', fontsize=14, fontweight='bold', pad=10)
    ax.set_ylabel('Score (%)')
    ax.set_xticks(x + width)
    ax.set_xticklabels(algos)
    ax.legend(loc='upper right', fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def main():
    print("=" * 60)
    print("  音乐推荐系统 - Matplotlib 离线分析报告生成")
    print("=" * 60)
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载数据
    print("\n[1/3] 加载数据...")
    ratings, song_genres, play_history, users, songs = load_data()
    print(f"  评分: {len(ratings)} 条, 流派: {len(song_genres)} 条")
    print(f"  播放记录: {len(play_history)} 条, 用户: {len(users)} 人, 歌曲: {len(songs)} 首")

    # 生成图表
    print("\n[2/3] 生成分析图表...")
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(os.path.join(output_dir, 'report'), exist_ok=True)

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Music Recommendation System - Data Analysis Report',
                 fontsize=18, fontweight='bold', y=0.98)

    plot_rating_distribution(axes[0, 0], ratings)
    plot_genre_distribution(axes[0, 1], song_genres)
    plot_play_trend(axes[0, 2], play_history)
    plot_user_activity(axes[1, 0], play_history)
    plot_language_distribution(axes[1, 1], songs)
    plot_algorithm_comparison(axes[1, 2], output_dir)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # 保存
    report_path = os.path.join(output_dir, 'report', 'analysis_report.png')
    fig.savefig(report_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"\n[3/3] 报告已保存")
    print(f"  综合报告: {report_path}")

    # 单独保存每个图表
    chart_configs = [
        ('rating_distribution', '评分分布', plot_rating_distribution, [ratings]),
        ('genre_distribution', '流派占比', plot_genre_distribution, [song_genres]),
        ('play_trend', '播放趋势', plot_play_trend, [play_history]),
        ('user_activity', '用户活跃度', plot_user_activity, [play_history]),
        ('language_distribution', '语言分布', plot_language_distribution, [songs]),
    ]

    for name, title, func, args in chart_configs:
        fig_single, ax_single = plt.subplots(1, 1, figsize=(8, 6))
        func(ax_single, *args)
        single_path = os.path.join(output_dir, 'report', f'{name}.png')
        fig_single.savefig(single_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig_single)
        print(f"  {title}: {single_path}")

    print(f"\n  完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
