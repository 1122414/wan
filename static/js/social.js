document.addEventListener('DOMContentLoaded', function () {
  const myChart = echarts.init(
    document.getElementById('social-chart-container')
  )

  loadChartData(myChart)
  loadhottData()
  // loadhottData(topicChart)

  function loadChartData(myChart) {
    fetch('/service/social/social_graph')
      .then((response) => {
        if (!response.ok)
          throw new Error(`HTTP错误! 状态码: ${response.status}`)
        return response.json()
      })
      .then((result) => {
        if (result.code !== 200) throw new Error('接口返回非200状态')
        console.log('节点数量:', result.data.nodes.length)
        console.log('边数量:', result.data.edges.length)
        console.log('边示例:', result.data.edges)

        // 构建完整配置项
        const option = {
          title: {
            text: '社交网络威胁关系图',
            left: 'center',
            textStyle: {
              color: '#333',
              fontSize: 18,
            },
          },
          tooltip: {
            trigger: 'item',
            formatter: function (params) {
              if (params.dataType === 'node') {
                const { area, threaten_level } = params.data.properties || {}
                return `
                <strong>${params.name}</strong><br>
                地区: ${area || '未知'}<br>
                威胁等级: ${threaten_level || '未知'}
              `
              } else {
                return `${params.source} → ${params.target}`
              }
            },
          },
          legend: {
            data: ['用户节点', '可疑组织'],
            bottom: 10,
          },
          animationDuration: 1500,
          animationEasingUpdate: 'quinticInOut',

          series: [
            {
              type: 'graph',
              layout: 'force',
              force: {
                repulsion: 5000,
                edgeLength: [10, 50],
                gravity: 0.05,
              },
              symbolSize: (node) => {
                const baseSize = node.value || 10
                return Math.max(10, Math.min(baseSize, 50))
              },
              roam: true,
              label: {
                show: true,
                position: 'right',
              },
              edgeSymbol: ['circle', 'arrow'],
              edgeSymbolSize: [4, 10],
              data: result.data.nodes, // 设置节点数据
              links: result.data.edges, // 设置边数据
              categories: [
                { name: '用户节点', itemStyle: { color: '#5470c6' } },
                { name: '可疑组织', itemStyle: { color: '#ff7875' } },
              ],
              lineStyle: {
                // 线的颜色[ default: '#aaa' ]
                color: '#1f1f1f',
                // 线宽[ default: 1 ]
                width: 10,
                // 线的类型[ default: solid实线 ]   'dashed'虚线    'dotted'
                type: 'solid',
                // 图形透明度。支持从 0 到 1 的数字，为 0 时不绘制该图形。[ default: 0.5 ]
                opacity: 0.5,
                // 边的曲度，支持从 0 到 1 的值，值越大曲度越大。[ default: 0 ]
                curveness: 0.5,
              },

              // 增强边配置
              edgeLabel: {
                show: true,
                formatter: '{c}',
                fontSize: 10,
              },
              emphasis: {
                lineStyle: {
                  width: 3,
                },
              },
            },
          ],
        }
        // 应用配置
        myChart.setOption(option)

        // 添加数据高亮
        myChart.on('mouseover', (params) => {
          if (params.dataType === 'node') {
            const { area, threaten_level } = params.data.properties || {}
            myChart.dispatchAction({
              type: 'showTip',
              seriesIndex: 0,
              dataIndex: params.dataIndex,
              name: params.name,
              content: `地区: ${area || '未知'}<br/>威胁等级: ${
                threaten_level || '未知'
              }`,
            })
          }
        })
      })
      .catch((error) => {
        console.error('图表加载失败:', error)
        // 显示降级内容
        const container = document.querySelector('.chart-container')
        if (container) {
          container.innerHTML = `
          <div class="chart-error" style="text-align: center; padding: 40px;">
            <i class="bi bi-exclamation-circle text-danger fs-1"></i>
            <p class="mt-3">图表加载失败</p>
            <p class="text-muted small">${error.message}</p>
            <button class="btn btn-sm btn-outline-primary mt-2" onclick="location.reload()">
              重新加载
            </button>
          </div>
        `
        }
      })
  }

  function loadhottData() {
    // 加载热门话题趋势数据
    fetch('/service/social/topic_trends')
    var chart = echarts.init(
      document.getElementById('hot-chart-placeholder'),
      'white',
      {
        renderer: 'canvas',
      }
    )
    $.ajax({
      type: 'GET',
      url: 'http://127.0.0.1:5000/service/social/topic_trends',
      dataType: 'json',
      success: function (result) {
        console.log(result)
        chart.setOption(result)
      },
    }).catch((error) => {
      console.error('加载热门话题趋势失败:', error)
      const container = document.getElementById('hot-chart-placeholder')
      container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-exclamation-circle text-danger fs-1"></i>
                <p class="mt-3">加载失败</p>
                <button class="btn btn-sm btn-outline-primary mt-2" onclick="location.reload()">
                    重新加载
                </button>
            </div>
        `
    })
  }
})
