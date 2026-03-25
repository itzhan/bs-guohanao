-- ============================================================
-- Hive SQL 数据分析查询样例
-- 说明: 以下查询在 Hive/Spark SQL 中等价执行
--       实际系统使用 PySpark 的 Spark SQL 替代 Hive
-- ============================================================

-- 1. 歌曲播放量排行 Top 20
SELECT s.id, s.title, a.name AS artist_name, s.play_count, s.avg_rating
FROM songs s
JOIN artists a ON s.artist_id = a.id
WHERE s.status = 1
ORDER BY s.play_count DESC
LIMIT 20;

-- 2. 流派播放热度分析
SELECT g.name AS genre_name,
       COUNT(sg.song_id) AS song_count,
       SUM(s.play_count) AS total_plays,
       ROUND(AVG(s.avg_rating), 2) AS avg_rating
FROM genres g
JOIN song_genre sg ON g.id = sg.genre_id
JOIN songs s ON sg.song_id = s.id
WHERE s.status = 1
GROUP BY g.name
ORDER BY total_plays DESC;

-- 3. 用户活跃度分析（月活/日活）
SELECT DATE_FORMAT(ph.created_at, '%Y-%m') AS month,
       COUNT(DISTINCT ph.user_id) AS monthly_active_users,
       COUNT(ph.id) AS total_plays
FROM play_history ph
GROUP BY DATE_FORMAT(ph.created_at, '%Y-%m')
ORDER BY month DESC;

-- 4. 评分分布统计
SELECT FLOOR(r.score) AS rating_level,
       COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ratings), 2) AS percentage
FROM ratings r
GROUP BY FLOOR(r.score)
ORDER BY rating_level;

-- 5. 用户偏好分析（Top 流派）
SELECT u.username,
       g.name AS favorite_genre,
       COUNT(*) AS listen_count
FROM play_history ph
JOIN users u ON ph.user_id = u.id
JOIN songs s ON ph.song_id = s.id
JOIN song_genre sg ON s.id = sg.song_id
JOIN genres g ON sg.genre_id = g.id
GROUP BY u.username, g.name
ORDER BY u.username, listen_count DESC;

-- 6. 评论情感分析统计
SELECT s.title,
       COUNT(c.id) AS comment_count,
       ROUND(AVG(c.sentiment_score), 3) AS avg_sentiment,
       SUM(CASE WHEN c.sentiment_label = '正向' THEN 1 ELSE 0 END) AS positive_count,
       SUM(CASE WHEN c.sentiment_label = '中性' THEN 1 ELSE 0 END) AS neutral_count,
       SUM(CASE WHEN c.sentiment_label = '负向' THEN 1 ELSE 0 END) AS negative_count
FROM comments c
JOIN songs s ON c.song_id = s.id
WHERE c.status = 1
GROUP BY s.title
HAVING comment_count >= 5
ORDER BY avg_sentiment DESC;

-- 7. 推荐算法覆盖率分析
SELECT r.algorithm,
       COUNT(DISTINCT r.user_id) AS covered_users,
       COUNT(DISTINCT r.song_id) AS covered_songs,
       ROUND(AVG(r.score), 3) AS avg_score,
       (SELECT COUNT(DISTINCT id) FROM users WHERE role = 'user') AS total_users,
       ROUND(COUNT(DISTINCT r.user_id) * 100.0 /
             (SELECT COUNT(DISTINCT id) FROM users WHERE role = 'user'), 1) AS user_coverage_pct
FROM recommendations r
GROUP BY r.algorithm;

-- 8. 歌手作品统计
SELECT a.name AS artist_name,
       a.region,
       COUNT(s.id) AS song_count,
       SUM(s.play_count) AS total_plays,
       ROUND(AVG(s.avg_rating), 2) AS avg_rating
FROM artists a
LEFT JOIN songs s ON a.id = s.artist_id AND s.status = 1
GROUP BY a.name, a.region
ORDER BY total_plays DESC
LIMIT 20;

-- 9. 语言分布统计
SELECT COALESCE(s.language, '未知') AS language,
       COUNT(*) AS song_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM songs WHERE status = 1), 1) AS percentage
FROM songs s
WHERE s.status = 1
GROUP BY s.language
ORDER BY song_count DESC;

-- 10. 用户行为漏斗分析
SELECT '注册用户' AS stage, COUNT(*) AS count FROM users WHERE role = 'user'
UNION ALL
SELECT '有播放记录', COUNT(DISTINCT user_id) FROM play_history
UNION ALL
SELECT '有评分记录', COUNT(DISTINCT user_id) FROM ratings
UNION ALL
SELECT '有收藏记录', COUNT(DISTINCT user_id) FROM favorites
UNION ALL
SELECT '有评论记录', COUNT(DISTINCT user_id) FROM comments WHERE status = 1;
