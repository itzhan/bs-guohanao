"""
评论情感分析服务
基于 SnowNLP 对评论文本进行情感倾向判断
"""


def analyze_sentiment(text):
    """
    分析文本情感倾向

    返回:
        score: 0.0-1.0 情感得分（越高越正向）
        label: 正向/中性/负向
    """
    if not text or not text.strip():
        return 0.5, '中性'

    try:
        from snownlp import SnowNLP
        s = SnowNLP(text)
        score = round(s.sentiments, 4)
    except ImportError:
        # SnowNLP 未安装时，返回中性默认值
        return 0.5, '中性'
    except Exception:
        return 0.5, '中性'

    # 三分类阈值
    if score >= 0.6:
        label = '正向'
    elif score <= 0.4:
        label = '负向'
    else:
        label = '中性'

    return score, label


def batch_analyze(texts):
    """批量分析情感（用于历史数据回填）"""
    return [analyze_sentiment(t) for t in texts]
