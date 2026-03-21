-- ============================================================
-- 基于大数据的音乐推荐与数据分析系统 - 数据库初始化脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS music_recommend DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE music_recommend;

SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;

-- -----------------------------------------------------------
-- 用户表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `recommendations`;
DROP TABLE IF EXISTS `user_preferences`;
DROP TABLE IF EXISTS `operation_logs`;
DROP TABLE IF EXISTS `play_history`;
DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `favorites`;
DROP TABLE IF EXISTS `ratings`;
DROP TABLE IF EXISTS `song_genre`;
DROP TABLE IF EXISTS `songs`;
DROP TABLE IF EXISTS `albums`;
DROP TABLE IF EXISTS `artists`;
DROP TABLE IF EXISTS `genres`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL COMMENT 'SHA-256加密密码',
    `nickname` VARCHAR(50) COMMENT '昵称',
    `email` VARCHAR(100) COMMENT '邮箱',
    `phone` VARCHAR(20) COMMENT '手机号',
    `avatar` VARCHAR(255) COMMENT '头像URL',
    `gender` SMALLINT DEFAULT 0 COMMENT '性别：0-未知 1-男 2-女',
    `age` INT COMMENT '年龄',
    `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：user/operator/admin',
    `status` SMALLINT DEFAULT 1 COMMENT '状态：0-禁用 1-正常',
    `preference_tags` TEXT COMMENT '音乐偏好标签(JSON)',
    `last_login` DATETIME COMMENT '最后登录时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- -----------------------------------------------------------
-- 流派表
-- -----------------------------------------------------------
CREATE TABLE `genres` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '流派名称',
    `description` VARCHAR(255) COMMENT '流派描述',
    `cover_image` VARCHAR(255) COMMENT '流派封面图',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='音乐流派表';

-- -----------------------------------------------------------
-- 歌手表
-- -----------------------------------------------------------
CREATE TABLE `artists` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '歌手名',
    `avatar` VARCHAR(255) COMMENT '歌手头像',
    `region` VARCHAR(50) COMMENT '地区：华语/欧美/日韩/其他',
    `description` TEXT COMMENT '歌手简介',
    `fans_count` INT DEFAULT 0 COMMENT '粉丝数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歌手表';

-- -----------------------------------------------------------
-- 专辑表
-- -----------------------------------------------------------
CREATE TABLE `albums` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(200) NOT NULL COMMENT '专辑名',
    `artist_id` INT NOT NULL COMMENT '歌手ID',
    `cover_image` VARCHAR(255) COMMENT '专辑封面',
    `release_date` DATE COMMENT '发行日期',
    `description` TEXT COMMENT '专辑简介',
    `song_count` INT DEFAULT 0 COMMENT '歌曲数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`artist_id`) REFERENCES `artists`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专辑表';

-- -----------------------------------------------------------
-- 歌曲表
-- -----------------------------------------------------------
CREATE TABLE `songs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL COMMENT '歌曲名',
    `artist_id` INT NOT NULL COMMENT '歌手ID',
    `album_id` INT COMMENT '专辑ID',
    `duration` INT COMMENT '时长(秒)',
    `cover_image` VARCHAR(255) COMMENT '封面图',
    `audio_url` VARCHAR(255) COMMENT '音频URL',
    `lyrics` TEXT COMMENT '歌词',
    `release_date` DATE COMMENT '发行日期',
    `language` VARCHAR(20) COMMENT '语言',
    `avg_rating` FLOAT DEFAULT 0.0 COMMENT '平均评分',
    `rating_count` INT DEFAULT 0 COMMENT '评分人数',
    `play_count` INT DEFAULT 0 COMMENT '播放次数',
    `favorite_count` INT DEFAULT 0 COMMENT '收藏次数',
    `status` SMALLINT DEFAULT 1 COMMENT '状态：0-下架 1-正常',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`artist_id`) REFERENCES `artists`(`id`),
    FOREIGN KEY (`album_id`) REFERENCES `albums`(`id`) ON DELETE SET NULL,
    INDEX `idx_play_count` (`play_count`),
    INDEX `idx_avg_rating` (`avg_rating`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歌曲表';

-- -----------------------------------------------------------
-- 歌曲-流派 多对多关联表
-- -----------------------------------------------------------
CREATE TABLE `song_genre` (
    `song_id` INT NOT NULL,
    `genre_id` INT NOT NULL,
    PRIMARY KEY (`song_id`, `genre_id`),
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`genre_id`) REFERENCES `genres`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歌曲-流派关联表';

-- -----------------------------------------------------------
-- 评分表
-- -----------------------------------------------------------
CREATE TABLE `ratings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `song_id` INT NOT NULL,
    `score` FLOAT NOT NULL COMMENT '评分(1-5)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_user_song_rating` (`user_id`, `song_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评分表';

-- -----------------------------------------------------------
-- 收藏表
-- -----------------------------------------------------------
CREATE TABLE `favorites` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `song_id` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_user_song_fav` (`user_id`, `song_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- -----------------------------------------------------------
-- 评论表
-- -----------------------------------------------------------
CREATE TABLE `comments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `song_id` INT NOT NULL,
    `content` TEXT NOT NULL COMMENT '评论内容',
    `parent_id` INT COMMENT '父评论ID(回复)',
    `like_count` INT DEFAULT 0 COMMENT '点赞数',
    `status` SMALLINT DEFAULT 1 COMMENT '状态：0-隐藏 1-正常',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`parent_id`) REFERENCES `comments`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- -----------------------------------------------------------
-- 播放记录表
-- -----------------------------------------------------------
CREATE TABLE `play_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `song_id` INT NOT NULL,
    `play_duration` INT DEFAULT 0 COMMENT '播放时长(秒)',
    `play_count` INT DEFAULT 1 COMMENT '播放次数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_updated` (`user_id`, `updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='播放记录表';

-- -----------------------------------------------------------
-- 用户偏好问卷表
-- -----------------------------------------------------------
CREATE TABLE `user_preferences` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `favorite_genres` TEXT COMMENT '喜爱流派(JSON数组)',
    `favorite_artists` TEXT COMMENT '喜爱歌手(JSON数组)',
    `listening_scenarios` TEXT COMMENT '听歌场景(JSON数组)',
    `preferred_language` VARCHAR(50) COMMENT '偏好语言',
    `mood_preference` VARCHAR(100) COMMENT '情绪偏好',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户偏好问卷表';

-- -----------------------------------------------------------
-- 推荐结果缓存表
-- -----------------------------------------------------------
CREATE TABLE `recommendations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `song_id` INT NOT NULL,
    `score` FLOAT COMMENT '推荐得分',
    `algorithm` VARCHAR(50) DEFAULT 'ALS' COMMENT '算法类型',
    `reason` VARCHAR(255) COMMENT '推荐理由',
    `is_read` TINYINT(1) DEFAULT 0 COMMENT '是否已查看',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_user_song_algo` (`user_id`, `song_id`, `algorithm`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`song_id`) REFERENCES `songs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推荐结果缓存表';

-- -----------------------------------------------------------
-- 操作日志表
-- -----------------------------------------------------------
CREATE TABLE `operation_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT COMMENT '操作用户ID',
    `username` VARCHAR(50) COMMENT '操作用户名',
    `action` VARCHAR(100) NOT NULL COMMENT '操作类型',
    `module` VARCHAR(50) COMMENT '操作模块',
    `description` TEXT COMMENT '操作描述',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `request_method` VARCHAR(10) COMMENT '请求方法',
    `request_url` VARCHAR(255) COMMENT '请求URL',
    `status` SMALLINT DEFAULT 1 COMMENT '操作状态：0-失败 1-成功',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_module` (`module`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
