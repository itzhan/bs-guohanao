"""
算法对比实验服务
读取实验结果 + 触发实验执行 + HDFS 状态查询
"""
import os
import json
import subprocess
from datetime import datetime


class ExperimentService:

    # 实验报告路径
    REPORT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'spark', 'output', 'comparison_report.json'
    )

    # Spark 脚本路径
    COMPARISON_SCRIPT = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'spark', 'algorithm_comparison.py'
    )

    @staticmethod
    def get_comparison_report():
        """读取算法对比实验报告"""
        # 优先从 /app/spark/output 读取（Docker 挂载目录）
        possible_paths = [
            '/app/spark/output/comparison_report.json',
            ExperimentService.REPORT_PATH,
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    return report
                except Exception as e:
                    return {'error': f'报告读取失败: {str(e)}'}

        return {
            'error': '尚未运行算法对比实验',
            'hint': '请先运行实验或点击"运行实验"按钮',
            'results': {},
        }

    @staticmethod
    def run_comparison():
        """触发运行算法对比实验"""
        # 查找脚本路径
        possible_scripts = [
            '/app/spark/algorithm_comparison.py',
            ExperimentService.COMPARISON_SCRIPT,
        ]

        script_path = None
        for path in possible_scripts:
            if os.path.exists(path):
                script_path = path
                break

        if not script_path:
            return {'error': '未找到算法对比脚本', 'status': 'failed'}

        try:
            result = subprocess.run(
                ['python', script_path],
                capture_output=True, text=True, timeout=300,
                env={**os.environ}
            )

            if result.returncode == 0:
                # 重新读取报告
                report = ExperimentService.get_comparison_report()
                return {
                    'status': 'success',
                    'message': '算法对比实验完成',
                    'output': result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
                    'report': report,
                }
            else:
                return {
                    'status': 'failed',
                    'error': result.stderr[-500:] if result.stderr else '未知错误',
                    'output': result.stdout[-500:] if result.stdout else '',
                }

        except subprocess.TimeoutExpired:
            return {'status': 'failed', 'error': '实验超时（>300秒）'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

    @staticmethod
    def get_hdfs_status():
        """获取 HDFS 存储状态"""
        hdfs_url = os.getenv('HDFS_URL', 'http://namenode:9870')
        hdfs_base_path = '/music/processed'

        try:
            from hdfs import InsecureClient
            client = InsecureClient(hdfs_url, user='root')

            # 列出 HDFS 上的文件
            files = client.list(hdfs_base_path, status=True)
            file_list = []
            total_size = 0
            for name, status in files:
                file_list.append({
                    'name': name,
                    'size': status.get('length', 0),
                    'type': status.get('type', 'FILE'),
                    'modificationTime': status.get('modificationTime', 0),
                })
                total_size += status.get('length', 0)

            return {
                'connected': True,
                'hdfs_url': hdfs_url,
                'base_path': hdfs_base_path,
                'files': file_list,
                'total_size': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'file_count': len(file_list),
            }

        except ImportError:
            return {
                'connected': False,
                'error': 'hdfs 库未安装',
                'hint': '在 Docker 容器内运行时自动可用',
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'hdfs_url': hdfs_url,
            }
