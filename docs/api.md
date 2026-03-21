# 基于大数据的音乐推荐与数据分析系统 - API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000`
- **认证方式**: JWT Bearer Token（Header: `Authorization: Bearer <token>`）
- **统一响应格式**: `{ "code": 200, "message": "操作成功", "data": {...} }`
- **分页响应格式**: `{ "code": 200, "data": { "records": [...], "total": N, "page": 1, "pageSize": 10 } }`

---

## 1. 认证模块 `/api/auth`

### POST /api/auth/register — 用户注册
**请求体**:
```json
{ "username": "newuser", "password": "123456", "nickname": "昵称", "email": "user@test.com" }
```

### POST /api/auth/login — 用户登录
**请求体**:
```json
{ "username": "user1", "password": "123456" }
```
**响应**:
```json
{ "code": 200, "data": { "token": "eyJhbGci...", "user": { "id": 3, "username": "user1", ... } } }
```

### GET /api/auth/info — 获取当前用户信息 🔒
### PUT /api/auth/update — 更新用户信息 🔒
### PUT /api/auth/password — 修改密码 🔒

---

## 2. 用户模块 `/api/user` 🔒

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/user/profile` | 获取个人信息 |
| GET | `/api/user/favorites?page=1&pageSize=10` | 收藏列表 |
| GET | `/api/user/history?page=1&pageSize=20` | 播放历史 |
| GET | `/api/user/preference` | 获取偏好 |
| POST | `/api/user/preference` | 保存偏好问卷 |

---

## 3. 歌曲模块 `/api/songs`

| 方法 | 路径 | 说明 | 参数 |
|---|---|---|---|
| GET | `/api/songs` | 歌曲列表 | page, pageSize, keyword, genreId, artistId, language, sortBy |
| GET | `/api/songs/:id` | 歌曲详情 | — |
| GET | `/api/songs/hot` | 热门歌曲 | limit |
| GET | `/api/songs/new` | 最新歌曲 | limit |
| GET | `/api/songs/top-rated` | 高评分歌曲 | limit |
| GET | `/api/songs/search` | 搜索歌曲 | keyword, page, pageSize |
| GET | `/api/songs/artists` | 歌手列表 | page, pageSize, region, keyword |
| GET | `/api/songs/artists/:id` | 歌手详情 | — |
| GET | `/api/songs/albums` | 专辑列表 | page, pageSize, artistId |
| GET | `/api/songs/genres` | 所有流派 | — |

---

## 4. 互动模块 `/api/interact`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/interact/rate` | 评分 `{songId, score}` | 🔒 |
| GET | `/api/interact/rating/:songId` | 获取我的评分 | 🔒 |
| POST | `/api/interact/favorite` | 收藏/取消 `{songId}` | 🔒 |
| GET | `/api/interact/favorite/check/:songId` | 检查收藏状态 | 🔒 |
| POST | `/api/interact/comment` | 发表评论 `{songId, content}` | 🔒 |
| GET | `/api/interact/comments/:songId` | 歌曲评论列表 | 公开 |
| DELETE | `/api/interact/comment/:id` | 删除评论 | 🔒 |
| POST | `/api/interact/play` | 记录播放 `{songId, duration}` | 🔒 |

---

## 5. 推荐模块 `/api/recommend`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/recommend/personal?limit=20` | 个性化推荐 | 🔒 |
| GET | `/api/recommend/similar/:songId?limit=10` | 相似歌曲 | 公开 |

---

## 6. 统计模块 `/api/stats`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/stats/overview` | 系统概览 |
| GET | `/api/stats/rating-distribution` | 评分分布 |
| GET | `/api/stats/genre-distribution` | 流派占比 |
| GET | `/api/stats/play-trend?days=30` | 播放趋势 |
| GET | `/api/stats/user-stats` | 用户个人分析 🔒 |
| GET | `/api/stats/top-artists?limit=10` | 热门歌手 |
| GET | `/api/stats/language-distribution` | 语言分布 |

---

## 7. 管理模块 `/api/admin` 🔒🛡️

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/admin/users` | 用户列表 | admin |
| PUT | `/api/admin/users/:id/status` | 禁用/启用 | admin |
| PUT | `/api/admin/users/:id/role` | 修改角色 | admin |
| GET | `/api/admin/songs` | 歌曲列表(含下架) | operator |
| POST | `/api/admin/songs` | 新增歌曲 | operator |
| PUT | `/api/admin/songs/:id` | 更新歌曲 | operator |
| DELETE | `/api/admin/songs/:id` | 下架歌曲 | operator |
| POST | `/api/admin/artists` | 新增歌手 | operator |
| PUT | `/api/admin/artists/:id` | 更新歌手 | operator |
| DELETE | `/api/admin/artists/:id` | 删除歌手 | admin |
| POST | `/api/admin/genres` | 新增流派 | operator |
| DELETE | `/api/admin/genres/:id` | 删除流派 | admin |
| GET | `/api/admin/comments` | 评论列表 | operator |
| PUT | `/api/admin/comments/:id/status` | 审核评论 | operator |
| GET | `/api/admin/logs` | 操作日志 | admin |

---

## 测试账号

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | admin | admin123 |
| 运营员 | operator | oper123 |
| 普通用户 | user1~user10 | 123456 |
