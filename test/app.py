from flask import Flask, render_template
from pyecharts.charts import WordCloud
from pyecharts import options as opts

app = Flask(__name__)

@app.route('/')
def show_wordcloud():
    # 示例数据
    data = [("Python", 100), ("Java", 80), ("JavaScript", 60)]
    
    # 创建词云图
    wordcloud = (
        WordCloud()
        .add(series_name="", data_pair=data, word_size_range=[20, 80])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云示例"))
    )
    
    # 将图表配置转为 JSON 字符串
    chart_json = wordcloud.dump_options_with_quotes()
    return render_template("wordcloud.html", chart_json=chart_json)

if __name__ == '__main__':
    app.run(debug=True)