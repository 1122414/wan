from inspect import iscode
import json
import random
from markupsafe import Markup
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models import IntelligenceModel  # 假设有情报模型
from exts import db
from exts import mail
from exts import redis
from flask_mail import Message
from sqlalchemy import or_
from pyecharts.charts import Graph
from pyecharts.commons.utils import JsCode
from pyecharts.charts import WordCloud, Pie, Line, Bar
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
    '4': '政治军事',
    '5': 'APT攻击',
    '6': '供应链攻击',
    '7': '勒索软件',
    '8': '恶意程序',
    '9': '数据泄露',
    '10': '网络诈骗',
    '11': '色情',
    '12': '诈骗',
    '13': '赌博',
    '14': '零日漏洞',
    '15': '黑客工具',
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
    print(wordcloud_html)
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
    
    # 创建词云图时直接添加点击事件处理
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(
            theme=ThemeType.DARK,
            width="100%",
            height="400px",
            animation_opts=opts.AnimationOpts(animation=False)
        ))
        .add(
            series_name="热点词云", 
            data_pair=words, 
            word_size_range=[12, 60],
            shape='circle',
            tooltip_opts=opts.TooltipOpts(
                formatter=JsCode(
                    "function(params) {"
                    "   return params.name + ': ' + params.value;"
                    "}"
                )
            ),    
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="热点词云"),
            tooltip_opts=opts.TooltipOpts(
                trigger="item"
            )
        )
        .set_series_opts(
            emphasis_opts=opts.EmphasisOpts(
                itemstyle_opts=opts.ItemStyleOpts(
                    border_color='#fff', 
                    border_width=1
                )
            )
        )
        .add_js_funcs(
        """
        // 获取图表实例
            var chart = echarts.init(document.querySelector('.chart-container'));
            
            // 添加点击事件监听
            chart.on('click', function(params) {
                console.log('词云点击:', params.name);
                window.location.href = '/service/intelligence?keyword=' + params.name;
            });
        """
        )
    )
    
    # 返回词云HTML，不再添加额外的JavaScript代码
    return Markup(wordcloud.render_embed())

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
            .limit(10000) \
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
    # 在返回数据中添加搜索链接
    formatted_data = [{
        'word': word, 
        'count': count,
        'search_url': f"/service/intelligence?keyword={word}"  # 添加搜索链接
    } for word, count in word_freq]

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
    redis.setex(cache_key, 24*3600, json.dumps(response_data))
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

# 关系图
@bp.route('/social/social_graph', methods=['GET', 'POST'])
def social_graph():
    # 查询所有情报数据
    intelligences = IntelligenceModel.query.limit(10000).all()
    
    # 构建节点和边
    nodes = []
    edges = []
    user_count = {}
    org_count = {}
    
    # 颜色映射表 (按地区)
    area_colors = {
        "北京": "#5470c6",
        "上海": "#91cc75",
        "广东": "#fac858",
        "江苏": "#ee6666",
        "浙江": "#73c0de",
        "其他": "#3ba272"
    }
    
    # 威胁等级映射
    threat_size = {"高": 30, "中": 20, "低": 10}
    
    # 在social_graph函数中修改节点生成逻辑
    for intel in intelligences:
        if intel.user_name:
            user_key = f"用户_{intel.user_name}"
            if user_key not in user_count:
                nodes.append({
                    "name": user_key,
                    "value": threat_size.get(intel.threaten_level, 10),  # 确保是数值
                    "category": "用户节点",  # 添加分类字段
                    "itemStyle": {"color": area_colors.get(intel.area, area_colors["其他"])},
                    "properties": {  # 添加属性字段
                        "area": intel.area,
                        "threaten_level": intel.threaten_level
                    }
                })
                user_count[user_key] = 1
        
        if intel.suspicious_organization:
            org_key = f"组织_{intel.suspicious_organization}"
            if org_key not in org_count:
                nodes.append({
                    "name": org_key,
                    "value": threat_size.get(intel.threaten_level, 10) * 1.5,  # 确保是数值
                    "category": "可疑组织",  # 添加分类字段
                    "itemStyle": {"color": "#ff7875"},
                    "properties": {  # 添加属性字段
                        "area": intel.area,
                        "threaten_level": intel.threaten_level
                    }
                })
                org_count[org_key] = 1
    
    # 生成边
    num_edges = len(nodes)  # 根据节点数量生成相应数量的边
    for _ in range(num_edges):
        source = random.choice(nodes)
        target = random.choice(nodes)
        
        # 确保 source 和 target 不是同一个节点且边不存在
        while source['name'] == target['name'] or any(e['source'] == source['name'] and e['target'] == target['name'] for e in edges):
            target = random.choice(nodes)
        
        edges.append({
            "source": source['name'],
            "target": target['name'],
        })
    
    # 创建微博风格关系图
    graph = (
        Graph(init_opts=opts.InitOpts(theme="white", width="100%", height="600px"))
        .add(
            "",
            nodes,
            edges,
            repulsion=5000,
            layout="circular",
            is_rotate_label=True,
            linestyle_opts=opts.LineStyleOpts(curve=0.2, width=1.5),
            label_opts=opts.LabelOpts(position="right"),
            edge_symbol=["circle", "arrow"],
            edge_symbol_size=[2, 8],
            # 修复 categories 格式
            categories=[  
                {"name": "用户节点"}, 
                {"name": "可疑组织"}
            ]
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="社交网络威胁关系图"),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_right="2%",
                pos_top="middle"
            ),
            tooltip_opts=opts.TooltipOpts(formatter="{b}<br/>类型: {c}")
        )
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'nodes': nodes,
            'edges': edges
        }
    })


# 在social_graph路由后面添加
@bp.route('/social/topic_trends', methods=['GET'])
def get_topic_trends():
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # 查询数据
    intelligences = IntelligenceModel.query.filter(
        IntelligenceModel.insert_time >= start_date,
        IntelligenceModel.insert_time <= end_date
    ).order_by(IntelligenceModel.insert_time.desc()).limit(1000).all()

    # 使用jieba分词提取关键词
    import jieba
    import jieba.analyse
    from collections import defaultdict

    # 按周统计
    time_periods = []
    current_date = start_date
    while current_date <= end_date:
        # 添加边界检查：如果当前日期已经等于结束日期，直接添加最后一天并退出
        if current_date == end_date:
            time_periods.append((current_date, current_date))
            break
        
        period_end = current_date + timedelta(days=7)
        
        # 如果计算出的结束日期超过总结束日期，则使用总结束日期
        if period_end > end_date:
            period_end = end_date
        
        time_periods.append((current_date, period_end))
        
        # 更新当前日期，确保向前推进
        current_date = period_end + timedelta(days=1)
        
        # 防止日期超过总结束日期
        if current_date > end_date:
            break
    
    # 初始化结果
    trends_data = {
        'periods': [period[0].strftime('%m-%d') for period in time_periods],
        'topics': defaultdict(list)
    }
    
    # 停用词
    stopwords = {
        '加入', '我们', '欢迎', '联系', '需要', '合作', '一起', '可以', 
        '进行', '提供', '服务', '方式', '了解', '详情', '请加', '添加',
        '咨询', '获取', '点击', '关注', '扫描', '二维码', '进群', '频道',
        '谢谢', '您好', '请问', '帮助', '支持', '免费', '优惠', '活动'
    }
    
    # 对每个时间段进行处理
    for i, (period_start, period_end) in enumerate(time_periods):
        # 获取该时间段的内容
        period_contents = [
            intel.content for intel in intelligences 
            if period_start <= intel.insert_time < period_end
        ]
        
        # 合并内容
        all_text = ' '.join(period_contents)
        
        # 提取关键词
        if all_text:
            keywords = jieba.analyse.extract_tags(all_text, topK=5, withWeight=True)
            
            # 过滤停用词
            filtered_keywords = [(word, weight) for word, weight in keywords if word not in stopwords]
            
            # 更新趋势数据
            for word, weight in filtered_keywords[:5]:  # 取前5个关键词
                trends_data['topics'][word].append(round(weight * 100, 2))  # 将权重转换为百分比
                
                # 确保每个主题在每个时间段都有值
                if len(trends_data['topics'][word]) < i + 1:
                    # 填充缺失的时间段
                    trends_data['topics'][word].extend([0] * (i + 1 - len(trends_data['topics'][word])))
    
    # 确保所有主题在所有时间段都有值
    for topic in trends_data['topics']:
        if len(trends_data['topics'][topic]) < len(time_periods):
            trends_data['topics'][topic].extend([0] * (len(time_periods) - len(trends_data['topics'][topic])))
    


    # 创建柱状图
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(trends_data['periods'])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="热门话题趋势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(pos_top="5%"),
            datazoom_opts=[
                opts.DataZoomOpts(range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100),
            ],
            yaxis_opts=opts.AxisOpts(
                name="热度",
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(
                type_='category',
                axislabel_opts=opts.LabelOpts(rotate=45)  # 旋转 x 轴标签以避免重叠
            )
        )
    )

    # 添加每个话题的数据
    colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
    for i, (topic, values) in enumerate(trends_data['topics'].items()):
        bar.add_yaxis(
            series_name=topic,
            y_axis=values,
            itemstyle_opts=opts.ItemStyleOpts(color=colors[i % len(colors)]),
            label_opts=opts.LabelOpts(is_show=False),
        )
    print(bar.dump_options_with_quotes())
    return bar.dump_options_with_quotes()