import request from '../utils/request'

// 认证
export const login = (data) => request.post('/auth/login', data)
export const register = (data) => request.post('/auth/register', data)
export const getUserInfo = () => request.get('/auth/info')
export const updateUserInfo = (data) => request.put('/auth/update', data)
export const changePassword = (data) => request.put('/auth/password', data)

// 歌曲
export const getSongs = (params) => request.get('/songs', { params })
export const getSongDetail = (id) => request.get(`/songs/${id}`)
export const getHotSongs = (limit = 20) => request.get('/songs/hot', { params: { limit } })
export const getNewSongs = (limit = 20) => request.get('/songs/new', { params: { limit } })
export const getTopRated = (limit = 20) => request.get('/songs/top-rated', { params: { limit } })
export const searchSongs = (params) => request.get('/songs/search', { params })
export const getArtists = (params) => request.get('/songs/artists', { params })
export const getArtistDetail = (id) => request.get(`/songs/artists/${id}`)
export const getGenres = () => request.get('/songs/genres')

// 互动
export const rateSong = (data) => request.post('/interact/rate', data)
export const getMyRating = (songId) => request.get(`/interact/rating/${songId}`)
export const toggleFavorite = (songId) => request.post('/interact/favorite', { songId })
export const checkFavorite = (songId) => request.get(`/interact/favorite/check/${songId}`)
export const addComment = (data) => request.post('/interact/comment', data)
export const getComments = (songId, params) => request.get(`/interact/comments/${songId}`, { params })
export const deleteComment = (id) => request.delete(`/interact/comment/${id}`)
export const recordPlay = (data) => request.post('/interact/play', data)

// 推荐
export const getRecommendations = (limit = 20) => request.get('/recommend/personal', { params: { limit } })
export const getSimilarSongs = (songId, limit = 10) => request.get(`/recommend/similar/${songId}`, { params: { limit } })

// 用户
export const getFavorites = (params) => request.get('/user/favorites', { params })
export const getHistory = (params) => request.get('/user/history', { params })
export const getPreference = () => request.get('/user/preference')
export const savePreference = (data) => request.post('/user/preference', data)

// 统计
export const getOverview = () => request.get('/stats/overview')
export const getRatingDistribution = () => request.get('/stats/rating-distribution')
export const getGenreDistribution = () => request.get('/stats/genre-distribution')
export const getPlayTrend = (days = 30) => request.get('/stats/play-trend', { params: { days } })
export const getUserStats = () => request.get('/stats/user-stats')
export const getTopArtists = (limit = 10) => request.get('/stats/top-artists', { params: { limit } })
export const getLanguageDistribution = () => request.get('/stats/language-distribution')
