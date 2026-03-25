import request from '../utils/request'

export const login = (data) => request.post('/auth/login', data)
export const getUserInfo = () => request.get('/auth/info')

// 用户管理
export const getUsers = (params) => request.get('/admin/users', { params })
export const updateUserStatus = (id, status) => request.put(`/admin/users/${id}/status`, { status })
export const updateUserRole = (id, role) => request.put(`/admin/users/${id}/role`, { role })

// 歌曲管理
export const getSongs = (params) => request.get('/admin/songs', { params })
export const createSong = (data) => request.post('/admin/songs', data)
export const updateSong = (id, data) => request.put(`/admin/songs/${id}`, data)
export const deleteSong = (id) => request.delete(`/admin/songs/${id}`)

// 歌手管理
export const getArtists = (params) => request.get('/songs/artists', { params })
export const createArtist = (data) => request.post('/admin/artists', data)
export const updateArtist = (id, data) => request.put(`/admin/artists/${id}`, data)
export const deleteArtist = (id) => request.delete(`/admin/artists/${id}`)

// 流派管理
export const getGenres = () => request.get('/songs/genres')
export const createGenre = (data) => request.post('/admin/genres', data)
export const deleteGenre = (id) => request.delete(`/admin/genres/${id}`)

// 评论管理
export const getComments = (params) => request.get('/admin/comments', { params })
export const updateCommentStatus = (id, status) => request.put(`/admin/comments/${id}/status`, { status })

// 操作日志
export const getLogs = (params) => request.get('/admin/logs', { params })

// 统计
export const getOverview = () => request.get('/stats/overview')
export const getRatingDistribution = () => request.get('/stats/rating-distribution')
export const getGenreDistribution = () => request.get('/stats/genre-distribution')
export const getPlayTrend = (days) => request.get('/stats/play-trend', { params: { days } })
export const getTopArtists = (limit) => request.get('/stats/top-artists', { params: { limit } })
export const getLanguageDistribution = () => request.get('/stats/language-distribution')

// 用户画像
export const getPortraitOverview = () => request.get('/portrait/overview')
export const getPortraitPreferences = () => request.get('/portrait/preferences')
export const getPortraitActivity = () => request.get('/portrait/activity')
export const getPortraitUser = (id) => request.get(`/portrait/${id}`)

// 推荐策略
export const getStrategyMetrics = () => request.get('/strategy/metrics')
export const getStrategyConfig = () => request.get('/strategy/config')
export const updateStrategyConfig = (data) => request.put('/strategy/config', data)

// 异常预警
export const getAlertList = (days) => request.get('/alert/list', { params: { days } })
export const getAlertStats = () => request.get('/alert/stats')

// 算法对比实验
export const getExperimentComparison = () => request.get('/experiment/comparison')
export const runExperiment = () => request.post('/experiment/run')
export const getHdfsStatus = () => request.get('/experiment/hdfs-status')

// 行为日志（MongoDB）
export const getBehaviorLogs = (params) => request.get('/behavior/logs', { params })
export const getBehaviorStats = () => request.get('/behavior/stats')

