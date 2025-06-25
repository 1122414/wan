import json
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models import IntelligenceModel  # 假设有情报模型
from exts import db
from exts import mail
from exts import redis
from flask_mail import Message
from sqlalchemy import or_
from pyecharts.charts import WordCloud, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB  # 添加MultinomialNB导入



bp = Blueprint("service", __name__, url_prefix="/service")

# 态势感知
# 主题情报汇总
@bp.route('/situation', methods=['GET', 'POST'])
def situation():
  return render_template('situation.html')

@bp.route('/situation/alert_info_total', methods=['GET'])
def alert_info_total():
    # 查询预警信息数量（示例逻辑，具体根据实际需求调整）
    total = IntelligenceModel.query.filter(IntelligenceModel.threaten_level != 'low').count()
    return jsonify({'code': 200, 'data': {'total': total}})

@bp.route('/situation/current_monitor_total', methods=['GET'])
def current_monitor_total():
    time_range = request.args.get('time_range', 'all')

    # 根据时间范围构建查询
    from datetime import datetime, timedelta
    now = datetime.now()
    if time_range == 'all':
        total = IntelligenceModel.query.count()
        return jsonify({'code': 200, 'data': {'total': total}})
    if time_range == '7days':
        start_date = now - timedelta(days=7)
    elif time_range == '24hours':
        start_date = now - timedelta(hours=24)
    elif time_range == '30days':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)

    # 查询当前监测总数（示例逻辑，具体根据实际需求调整）
    total = IntelligenceModel.query.filter(IntelligenceModel.insert_time >= start_date).count()
    return jsonify({'code': 200, 'data': {'total': total}})

@bp.route('/situation/handled_messages_total', methods=['GET'])
def handled_messages_total():
    # 查询处置消息数量（示例逻辑，具体根据实际需求调整）
    total = IntelligenceModel.query.filter(IntelligenceModel.status == 'handled').count()
    return jsonify({'code': 200, 'data': {'total': total}})

# 情报来源
@bp.route('/situation/intelligence_source_trend', methods=['GET'])
def intelligence_source_trend():
    time_range = request.args.get('time_range', '7days')

    # 根据时间范围构建查询
    from datetime import datetime, timedelta
    now = datetime.now()
    if time_range == '7days':
        start_date = now - timedelta(days=7)
    elif time_range == '24hours':
        start_date = now - timedelta(hours=24)
    elif time_range == '30days':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)

    # 查询数据（示例逻辑，具体根据实际需求调整）
    results = IntelligenceModel.query.filter(IntelligenceModel.insert_time >= start_date).all()

    dates = []
    telegram_data = []
    tor_data = []

    for result in results:
        date_str = result.insert_time.strftime('%Y-%m-%d')
        if date_str not in dates:
            dates.append(date_str)
            telegram_data.append(0)
            tor_data.append(0)

        index = dates.index(date_str)
        if result.source == 't':
            telegram_data[index] += 1
        elif result.source == 'tor':
            tor_data[index] += 1

    return jsonify({
        'code': 200,
        'data': {
            'dates': dates,
            'telegram': telegram_data,
            'tor': tor_data
        }
    })

@bp.route('/situation/new_suspect_data', methods=['GET'])
def new_suspect_data():
    time_range = request.args.get('time_range', '7days')

    # 根据时间范围构建查询
    from datetime import datetime, timedelta
    now = datetime.now()
    if time_range == '7days':
        start_date = now - timedelta(days=7)
    elif time_range == '24hours':
        start_date = now - timedelta(hours=24)
    elif time_range == '30days':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)

    # 查询数据（示例逻辑，具体根据实际需求调整）
    results = IntelligenceModel.query.filter(
        IntelligenceModel.insert_time >= start_date
    ).all()

    organizations = set()
    users = set()

    for result in results:
        if result.suspicious_organization:
            organizations.add(result.suspicious_organization)
        if result.suspicious_user:
            users.add(result.suspicious_user)

    return jsonify({
        'code': 200,
        'data': {
            'organizations': list(organizations),
            'users': list(users)
        }
    })

# 情报检索
@bp.route('/intelligence', methods=['GET', 'POST'])
def intelligence():
  return render_template('intelligence.html')

# 搜索功能
@bp.route('/intelligence/search', methods=['POST'])
def search_intelligence():
  # 获取搜索参数
  search_data = request.json
  keyword = search_data.get('keyword', '').strip()
  intel_type = search_data.get('type', '')
  time_range = search_data.get('time_range', '')

  page = search_data.get('page', 1)
  per_page = search_data.get('per_page', 10)

  type_mapping = {
    '1': '反恐维稳',
    '2': '黑灰产',
    '3': '走私贩毒',
    '4': '政治军事'
  }
  intel_type_name = type_mapping.get(intel_type, intel_type)

  time_mapping = {
    '1': '最近24小时',
    '2': '最近7天',
    '3': '最近30天',
    '4': '最近90天'
  }
  intel_time_name = time_mapping.get(time_range, time_range)

  # 构建查询
  query = IntelligenceModel.query

  # 关键词搜索（标题和内容）
  if keyword:
      query = query.filter(
          or_(
              IntelligenceModel.content.ilike(f'%{keyword}%')
          )
      )
  
  # 类型过滤
  if intel_type_name and intel_type_name != '所有类型':
      print(intel_type_name)
      query = query.filter(IntelligenceModel.label_name.ilike(f'%{intel_type_name}%') )
      
  # 时间范围过滤
  if intel_time_name != '所有时间':
    print(intel_time_name)
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        if intel_time_name == '最近24小时':
            start_date = now - timedelta(hours=24)
        elif intel_time_name == '最近7天':
            start_date = now - timedelta(days=7)
        elif intel_time_name == '最近30天':
            start_date = now - timedelta(days=30)
        elif intel_time_name == '最近90天':
            start_date = now - timedelta(days=90)
        else:
            start_date = None
    except Exception as e:
        print(f"时间范围处理错误: {e}")
        start_date = None

    if start_date:
      query = query.filter(IntelligenceModel.insert_time >= start_date)

  # # 执行查询
  # results = query.order_by(IntelligenceModel.insert_time.desc()).all()

  # # 格式化结果
  # intelligence_list = [{
  #     'id': item.id,
  #     'content': item.content,
  #     'insert_time': item.insert_time,
  #     'label_name': item.label_name,
  #     'user_name': item.user_name,
  #     'area': item.area,
  #     'threaten_level': item.threaten_level,
  # } for item in results]

  # 分页查询
  pagination = query.paginate(page=page, per_page=per_page,error_out=False)
  results = pagination.items

  intelligence_list = [{
      'id': item.id,
      'content': item.content,
      'insert_time': item.insert_time.strftime("%Y-%m-%d %H:%M:%S"),
      'label_name': item.label_name,
      'user_name': item.user_name,
      'area': item.area,
      'threaten_level': item.threaten_level,
  } for item in results]

  return jsonify({
        'code': 200,
        'data': intelligence_list,
        'pagination':{
           'total': pagination.total,       # 总记录数
           'current_page': pagination.page, # 当前页码
           'per_page': pagination.per_page, # 每页记录数
           'total_pages': pagination.pages  # 总页数
        }
        # 'total': pagination.total,
        # 'current_page': pagination.page,
        # 'per_page': pagination.per_page,
        # 'total_pages': pagination.pages
      })

# 热点分析
@bp.route('/hotspot', methods=['GET', 'POST'])
def hotspot():
    wordcloud_html = get_wordcloud_html()
    stats_html = get_stats_html()
    return render_template('hotspot.html', 
                           wordcloud_html=wordcloud_html,
                           stats_html=stats_html)

# 热点词云
@bp.route('/hotspot/wordcloud_html')
def get_wordcloud_html():
    # 获取词云数据
    data = get_wordcloud_data().json['data']
    if not data:
        return "<div class='text-center py-5'>暂无词云数据</div>"
    
    words = [(d['word'], d['count']) for d in data]
    
    # 创建词云图
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(
            theme=ThemeType.DARK,
            width="100%",
            height="400px"
        ))
        .add(
            series_name="热点词云", 
            data_pair=words, 
            word_size_range=[12, 60],
            shape='circle'
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="热点词云"),
            tooltip_opts=opts.TooltipOpts(is_show=True)
        )
    )
    return wordcloud.render_embed()

#热点统计
@bp.route('/hotspot/stats_html')
def get_stats_html():
    # 获取统计数据
    stats_data = get_hotspot_stats().json['data']['percent']
    if not stats_data:
        return "<div class='text-center py-5'>暂无统计数据</div>"
    
    data = list(stats_data.items())
    
    # 创建饼图
    pie = (
        Pie(init_opts=opts.InitOpts(
            theme=ThemeType.DARK,
            width="100%",
            height="400px"
        ))
        .add(
            series_name="热点分布",
            data_pair=data,
            radius=["50%", "70%"],
            label_opts=opts.LabelOpts(  # 直接在这里配置标签选项
                formatter="{b}: {c}%",
                position="outside",
                margin=8
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="热点统计"),
            legend_opts=opts.LegendOpts(
                orient="vertical", 
                pos_left="left",
                pos_top="middle"
            )
        )
        # .set_series_opts(  # 在这里配置系列选项
        #     label_opts=opts.LabelOpts(
        #         linestyle_opts=opts.LineStyleOpts(  # 配置标签线样式
        #             width=1,
        #             color="#ccc"
        #         )
        #     )
        # )
    )
    return pie.render_embed()

# 新增词云数据接口
@bp.route('/hotspot/wordcloud', methods=['GET'])
def get_wordcloud_data():
    # 检查缓存
    cache_key = 'wordcloud_data'
    cached_data = redis.get(cache_key)
    if cached_data:
        # 将缓存数据从字符串转换为 Python 对象（这里是列表）
        word_freq = json.loads(cached_data)
    else:
        # 获取所有情报内容
        contents = IntelligenceModel.query.with_entities(IntelligenceModel.content) \
            .order_by(IntelligenceModel.insert_time.desc()) \
            .limit(1000) \
            .all()

        # 如果没有内容，返回空
        if not contents:
            return jsonify({
                'code': 200,
                'data': []
            })

        # 使用jieba进行中文分词
        import jieba
        from collections import Counter
        import re

        # 合并所有内容
        all_text = ' '.join([c[0] for c in contents])

        # 黑灰产停用词列表 (新增)
        BLACK_GRAY_STOPWORDS = {
            '加入', '我们', '欢迎', '联系', '需要', '合作', '一起', '可以', 
            '进行', '提供', '服务', '方式', '了解', '详情', '请加', '添加',
            '咨询', '获取', '点击', '关注', '扫描', '二维码', '进群', '频道',
            '谢谢', '您好', '请问', '帮助', '支持', '免费', '优惠', '活动','成为','确保','验证','问题','务必','报告','之前','群内','链接','你们','你'
        }

        # 分词并过滤停用词 (优化)
        words = jieba.cut(all_text)
        # 双重过滤：长度+字符类型+停用词
        filtered_words = [
            word for word in words 
            if len(word) > 1 
            and re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', word) 
            and word not in BLACK_GRAY_STOPWORDS  # 新增停用词过滤
        ]

        # 统计词频 (限制为前50个)
        word_freq = Counter(filtered_words).most_common(20)  # 减少返回数量

        # 缓存到Redis（延长至24小时）
        redis.setex(cache_key, 24*3600, json.dumps(word_freq))

    # 将词频列表转换为前端期望的格式
    formatted_data = [{'word': word, 'count': count} for word, count in word_freq]

    return jsonify({
        'code': 200,
        'data': formatted_data
    })

# 新增热点事件接口
@bp.route('/hotspot/events', methods=['GET'])
def get_hotspot_events():
    source = request.args.get('source', '')  # 't' 或 'tor'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 4, type=int)
    
    # 构建查询
    query = IntelligenceModel.query
    
    # 按来源过滤
    if source in ['t', 'tor']:
        query = query.filter(IntelligenceModel.source == source)
    
    # 排序：先按威胁等级（高->中->低），再按时间倒序
    from sqlalchemy import case
    level_order = case(
        (IntelligenceModel.threaten_level == '高', 3),
        (IntelligenceModel.threaten_level == '中', 2),
        (IntelligenceModel.threaten_level == '低', 1),
        else_=0
    )
    query = query.order_by(level_order.desc(), IntelligenceModel.insert_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items
    
    events = [{
        'id': item.id,
        'title': item.content[:50] + '...' if len(item.content) > 50 else item.content,
        'content': item.content,
        'insert_time': item.insert_time.strftime("%Y-%m-%d"),
        'threaten_level': item.threaten_level,
        'source': item.source,
        'views': 0,  # 后续可添加实际浏览数据
        'comments': 0  # 后续可添加评论数据
    } for item in results]
    
    return jsonify({
        'code': 200,
        'data': events,
        'pagination': {
            'total': pagination.total,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages
        }
    })

# 新增热点统计接口
@bp.route('/hotspot/stats', methods=['GET'])
def get_hotspot_stats():
    cache_key = 'hotspot_stats'
    cached_data = redis.get(cache_key)
    # 确保缓存数据格式正确
    if cached_data:
        try:
            data = json.loads(cached_data)
            # 添加格式验证
            if 'stats' in data and 'percent' in data:
                return jsonify({
                    'code': 200,
                    'data': data
                })
        except Exception as e:
            print(f"缓存数据解析错误: {e}")
            # 错误时清除缓存
            redis.delete(cache_key)
    
    # 获取所有情报内容
    all_intels = IntelligenceModel.query.all()
    contents = [intel.content for intel in all_intels]

    # 定义热点类别及其训练数据，确保每个类别的关键词数量平衡
    categories = {
        'APT攻击': ['APT', '高级威胁', '国家支持', '定向攻击', '持续性威胁', '间谍活动'],
        '供应链攻击': ['供应链', '依赖投毒', '第三方漏洞', '供应商入侵', '软件依赖', '升级通道'],
        '勒索软件': ['勒索', '加密', '赎金', 'blackcat', 'lockbit', '文件加密'],
        '数据泄露': ['数据外泄', '信息泄露', '隐私泄露', '个人信息', '数据库泄露', '账户信息'],
        '零日漏洞': ['零日漏洞', '0day', '未公开漏洞', '未修补漏洞', '安全漏洞', '系统漏洞'],
        '网络诈骗': ['诈骗', '钓鱼', '仿冒', '欺诈', '电信诈骗', '网络诈骗'],
        '恶意程序': ['木马', '病毒', '蠕虫', '后门', '恶意软件', '挖矿程序'],
        '黑客工具': ['黑客工具', '漏洞利用', '攻击框架', '渗透工具', '网络扫描', '密码破解'],
        # 新增黑灰产分类
        '色情': ['色情', '成人', '淫秽', '黄色', '情色', 'AV', '会所'],
        '赌博': ['赌博', '赌球', '赌马', '赌场', '下注'],
        '诈骗': ['诈骗', '钓鱼', '仿冒', '中奖', '转账']
    }

    # 构建训练数据
    train_data = []
    train_labels = []
    for category, keywords in categories.items():
        for keyword in keywords:
            train_data.append(keyword)
            train_labels.append(category)

    # 训练模型并添加权重
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import LabelEncoder

    # 使用TF-IDF而不是简单的CountVectorizer
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),  # 考虑单词和词组
        max_features=1000
    )
    
    X_train = vectorizer.fit_transform(train_data)
    
    # 标签编码
    le = LabelEncoder()
    encoded_labels = le.fit_transform(train_labels)
    
    # 使用带有优化参数的MultinomialNB
    clf = MultinomialNB(
        alpha=0.1,  # 平滑参数
        fit_prior=True  # 学习类别先验概率
    ).fit(X_train, encoded_labels)

    # 预测类别
    X_test = vectorizer.transform(contents)
    predicted_proba = clf.predict_proba(X_test)
    predicted = le.inverse_transform([p.argmax() for p in predicted_proba])
    
    # 使用概率阈值过滤低置信度预测
    confidence_threshold = 0.3
    high_confidence_predictions = []
    for i, probs in enumerate(predicted_proba):
        max_prob = probs.max()
        if max_prob >= confidence_threshold:
            high_confidence_predictions.append(predicted[i])
        else:
            # 置信度低的样本归类为"其他"
            high_confidence_predictions.append("其他")
    predicted = high_confidence_predictions

    # 统计每个类别的出现次数
    stats = {}
    for category in categories.keys():
        stats[category] = sum(1 for p in predicted if p == category)

    # 计算总数和百分比
    total = sum(stats.values())
    stats_percent = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in stats.items()}

    # 对结果进行平衡处理
    min_percent = 5  # 设置最小占比
    for category in stats_percent:
        if stats_percent[category] < min_percent:
            stats_percent[category] = min_percent
            
    # 重新计算百分比使总和为100%
    total_percent = sum(stats_percent.values())
    stats_percent = {k: round(v / total_percent * 100, 1) for k, v in stats_percent.items()}
    
    # 更新response_data
    response_data = {
        'stats': stats,
        'percent': stats_percent
    }
    
    # 缓存结果（1小时）
    redis.setex(cache_key, 3600, json.dumps(response_data))
    return jsonify({
        'code': 200,
        'data': {
            'stats': stats,
            'percent': stats_percent
        }
    })

# 刷新词云缓存
@bp.route('/hotspot/refresh_cache', methods=['POST'])
def refresh_wordcloud_cache():
    cache_key = 'wordcloud_data'
    redis.delete(cache_key)
    return jsonify({
        'code': 200,
        'message': '词云缓存已刷新'
    })

# 社交网络
@bp.route('/social', methods=['GET', 'POST'])
def social():
  return render_template('social.html')
