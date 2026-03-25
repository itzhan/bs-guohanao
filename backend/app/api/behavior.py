"""
用户行为日志 API（从 MongoDB 读取）
"""
from flask import Blueprint, request
from app.utils.response import success_response, error_response
from app.utils.auth import operator_required
from app.extensions import mongo

behavior_bp = Blueprint('behavior', __name__)


@behavior_bp.route('/logs', methods=['GET'])
@operator_required
def get_behavior_logs():
    """获取用户行为日志（分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    user_id = request.args.get('userId', type=int)
    action = request.args.get('action')

    try:
        collection = mongo.get_collection('user_behaviors')

        # 构建查询条件
        query = {}
        if user_id:
            query['user_id'] = user_id
        if action:
            query['action'] = action

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort('timestamp', -1).skip(skip).limit(page_size)

        records = []
        for doc in cursor:
            records.append({
                'id': str(doc.get('_id', '')),
                'userId': doc.get('user_id'),
                'songId': doc.get('song_id'),
                'action': doc.get('action', ''),
                'duration': doc.get('duration', 0),
                'timestamp': doc['timestamp'].isoformat() if doc.get('timestamp') else None,
            })

        return success_response({
            'records': records,
            'total': total,
            'page': page,
            'pageSize': page_size,
        })
    except Exception as e:
        return success_response({'records': [], 'total': 0, 'page': 1, 'pageSize': page_size})


@behavior_bp.route('/stats', methods=['GET'])
@operator_required
def get_behavior_stats():
    """获取行为统计摘要"""
    try:
        collection = mongo.get_collection('user_behaviors')
        total = collection.count_documents({})

        # 按行为类型统计
        pipeline = [
            {'$group': {'_id': '$action', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
        ]
        action_stats = list(collection.aggregate(pipeline))

        return success_response({
            'totalLogs': total,
            'actionDistribution': [
                {'action': s['_id'], 'count': s['count']} for s in action_stats
            ],
        })
    except Exception:
        return success_response({'totalLogs': 0, 'actionDistribution': []})
