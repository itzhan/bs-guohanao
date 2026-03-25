"""
算法对比实验 API Blueprint
提供推荐算法对比实验结果的查询接口
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.experiment_service import ExperimentService

experiment_bp = Blueprint('experiment', __name__)


@experiment_bp.route('/comparison', methods=['GET'])
@jwt_required()
def get_comparison():
    """获取算法对比实验结果"""
    result = ExperimentService.get_comparison_report()
    return jsonify({'code': 200, 'data': result})


@experiment_bp.route('/run', methods=['POST'])
@jwt_required()
def run_experiment():
    """触发运行算法对比实验"""
    result = ExperimentService.run_comparison()
    return jsonify({'code': 200, 'data': result, 'message': '实验完成'})


@experiment_bp.route('/hdfs-status', methods=['GET'])
@jwt_required()
def hdfs_status():
    """获取 HDFS 存储状态"""
    result = ExperimentService.get_hdfs_status()
    return jsonify({'code': 200, 'data': result})
