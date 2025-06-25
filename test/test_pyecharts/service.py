from pyecharts.charts import WordCloud
from pyecharts import options as opts

# 示例数据
data = [("Python", 100), ("Java", 80), ("JavaScript", 60)]

# 创建词云图
wordcloud = (
    WordCloud()
    .add(series_name="", data_pair=data, word_size_range=[20, 80])
    .set_global_opts(title_opts=opts.TitleOpts(title="词云示例"))
)

# 生成 HTML 文件（注意：需设置 render_options={"echarts_events": True}）
wordcloud.render("wordcloud.html", render_options={"echarts_events": True})