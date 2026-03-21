"""
统一响应格式工具
"""
from flask import jsonify


def success_response(data=None, message='操作成功', code=200):
    """成功响应"""
    resp = {
        'code': code,
        'message': message,
        'data': data
    }
    return jsonify(resp), 200


def error_response(code=400, message='请求失败', data=None):
    """错误响应"""
    resp = {
        'code': code,
        'message': message,
        'data': data
    }
    http_code = 200
    if code == 401:
        http_code = 401
    elif code == 403:
        http_code = 403
    return jsonify(resp), http_code


def page_response(items, total, page, page_size):
    """分页响应"""
    return success_response({
        'records': items,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size
    })
