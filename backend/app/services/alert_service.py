"""
异常行为预警服务
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.interact import Rating, PlayHistory
from app.models.system import OperationLog


class AlertService:

    @staticmethod
    def get_stats():
        """预警概览统计"""
        alerts = AlertService.get_alerts()
        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        type_count = {}
        for a in alerts:
            severity_count[a['severity']] = severity_count.get(a['severity'], 0) + 1
            type_count[a['type']] = type_count.get(a['type'], 0) + 1

        return {
            'totalAlerts': len(alerts),
            'highCount': severity_count['high'],
            'mediumCount': severity_count['medium'],
            'lowCount': severity_count['low'],
            'typeDistribution': [{'name': k, 'value': v} for k, v in type_count.items()],
        }

    @staticmethod
    def get_alerts(days=7):
        """获取预警列表"""
        alerts = []
        since = datetime.now() - timedelta(days=days)

        # 1. 刷分检测：短时间内大量评分（1小时内 > 20条）
        rating_abuse = db.session.query(
            Rating.user_id,
            func.count(Rating.id).label('count'),
            func.min(Rating.created_at).label('first_time'),
            func.max(Rating.created_at).label('last_time'),
        ).filter(Rating.created_at >= since) \
            .group_by(Rating.user_id, func.date(Rating.created_at), func.hour(Rating.created_at)) \
            .having(func.count(Rating.id) > 20).all()

        for r in rating_abuse:
            user = User.query.get(r.user_id)
            alerts.append({
                'id': f'rating-{r.user_id}-{r.first_time}',
                'type': '刷分行为',
                'severity': 'high',
                'userId': r.user_id,
                'username': user.username if user else '未知',
                'description': f'用户 {user.username if user else r.user_id} 在1小时内评分 {r.count} 次',
                'count': r.count,
                'detectedAt': str(r.last_time),
            })

        # 2. 异常播放检测：播放时长 < 3秒且播放次数 > 50
        play_abuse = db.session.query(
            PlayHistory.user_id,
            func.count(PlayHistory.id).label('count'),
            func.avg(PlayHistory.play_duration).label('avg_dur'),
        ).filter(
            PlayHistory.created_at >= since,
            PlayHistory.play_duration < 3,
        ).group_by(PlayHistory.user_id) \
            .having(func.count(PlayHistory.id) > 50).all()

        for p in play_abuse:
            user = User.query.get(p.user_id)
            alerts.append({
                'id': f'play-{p.user_id}',
                'type': '刷量行为',
                'severity': 'high',
                'userId': p.user_id,
                'username': user.username if user else '未知',
                'description': f'用户 {user.username if user else p.user_id} 有 {p.count} 次极短播放（平均 {p.avg_dur:.1f}s）',
                'count': p.count,
                'detectedAt': str(datetime.now()),
            })

        # 3. 异常登录行为：短时间内大量失败登录（基于操作日志）
        login_fail = db.session.query(
            OperationLog.username,
            OperationLog.ip_address,
            func.count(OperationLog.id).label('count'),
            func.max(OperationLog.created_at).label('last_time'),
        ).filter(
            OperationLog.action == '登录',
            OperationLog.status == 0,
            OperationLog.created_at >= since,
        ).group_by(OperationLog.username, OperationLog.ip_address) \
            .having(func.count(OperationLog.id) > 10).all()

        for l in login_fail:
            alerts.append({
                'id': f'login-{l.username}-{l.ip_address}',
                'type': '异常登录',
                'severity': 'medium',
                'userId': None,
                'username': l.username or '未知',
                'description': f'用户 {l.username} 从 {l.ip_address} 登录失败 {l.count} 次',
                'count': l.count,
                'detectedAt': str(l.last_time),
            })

        # 4. 不活跃用户预警：注册超过30天但无任何行为
        inactive_cutoff = datetime.now() - timedelta(days=30)
        inactive_users = db.session.query(func.count(User.id)).filter(
            User.role == 'user',
            User.created_at < inactive_cutoff,
            ~User.id.in_(db.session.query(func.distinct(PlayHistory.user_id))),
            ~User.id.in_(db.session.query(func.distinct(Rating.user_id))),
        ).scalar() or 0

        if inactive_users > 0:
            alerts.append({
                'id': 'inactive-users',
                'type': '用户不活跃',
                'severity': 'low',
                'userId': None,
                'username': '-',
                'description': f'有 {inactive_users} 个用户注册超过30天但无任何行为记录',
                'count': inactive_users,
                'detectedAt': str(datetime.now()),
            })

        # 按严重程度排序
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        return alerts
