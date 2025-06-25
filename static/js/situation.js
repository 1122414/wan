$(document).ready(function () {
  // 安全事件趋势
  // 获取预警信息数量

  // 时间范围选择器变更事件
  $('#event-time-range-selector').change(function () {
    const timeRange = $(this).val()
    // 获取当前监测总数
    $.ajax({
      url: '/service/situation/current_monitor_total',
      method: 'GET',
      data: { time_range: timeRange },
      success: function (response) {
        $('#current-monitor-total').text(response.data.total)
      },
    })
  })

  $.ajax({
    url: '/service/situation/alert_info_total',
    method: 'GET',
    success: function (response) {
      $('#alert-info-counter').text(response.data.total)
    },
  })

  // 获取处置消息数量
  $.ajax({
    url: '/service/situation/handled_messages_total',
    method: 'GET',
    success: function (response) {
      $('#handled-messages-counter').text(response.data.total)
    },
  })

  // 获取当前监测总数
  $.ajax({
    url: '/service/situation/current_monitor_total',
    method: 'GET',
    success: function (response) {
      $('#current-monitor-total').text(response.data.total)
    },
  })

  // 更新时间戳
  function updateTimestamp() {
    const now = new Date()
    const timestamp = now.toLocaleString()
    $('#timestamp').text(timestamp)
  }

  // 每秒更新一次时间戳
  setInterval(updateTimestamp, 1000)

  // 情报来源趋势
  // 初始化 ECharts 实例
  var chartDom = document.getElementById('intelligence-source-trend-chart')
  var myChart = echarts.init(chartDom)

  // 配置项
  var option = {
    title: {
      text: '',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['telegram', 'tor'],
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [], // x轴数据
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: 'telegram',
        type: 'line',
        data: [], // telegram 数据
      },
      {
        name: 'tor',
        type: 'line',
        data: [], // tor 数据
      },
    ],
  }
  // 使用刚指定的配置项和数据显示图表。
  myChart.setOption(option)

  // 获取情报来源趋势数据
  function getIntelligenceSourceTrendData(timeRange) {
    $.ajax({
      url: '/service/situation/intelligence_source_trend',
      method: 'GET',
      data: { time_range: timeRange },
      success: function (response) {
        if (response.code === 200) {
          const data = response.data
          option.xAxis.data = data.dates
          option.series[0].data = data.telegram
          option.series[1].data = data.tor
          myChart.setOption(option)
        }
      },
    })
  }

  // 默认加载近七天的数据
  getIntelligenceSourceTrendData('7days')

  // 时间范围选择器变更事件
  $('#intelligence-time-range-selector').change(function () {
    console.log(1111)
    const timeRange = $(this).val()
    getIntelligenceSourceTrendData(timeRange)
  })

  // 最后一块
  // 获取新增可疑组织和用户数据
  function getNewSuspectData(timeRange) {
    $.ajax({
      url: '/service/situation/new_suspect_data',
      method: 'GET',
      data: { time_range: timeRange },
      success: function (response) {
        if (response.code === 200) {
          const data = response.data
          updateSuspectOrganizations(data.organizations)
          updateSuspectUsers(data.users)
        }
      },
    })
  }

  // 更新新增可疑组织列表
  function updateSuspectOrganizations(organizations) {
    const $organizationsList = $('#new-suspect-organizations')
    $organizationsList.empty()
    organizations.forEach((org) => {
      const listItem = $('<li class="list-group-item"></li>').text(org)
      $organizationsList.append(listItem)
    })
  }

  // 更新新增可疑用户列表
  function updateSuspectUsers(users) {
    const $usersList = $('#new-suspect-users')
    $usersList.empty()
    users.forEach((user) => {
      const listItem = $('<li class="list-group-item"></li>').text(user)
      $usersList.append(listItem)
    })
  }

  // 默认加载近七天的数据
  getNewSuspectData('7days')

  // 时间范围选择器变更事件
  $('#event-time-range-selector').change(function () {
    const timeRange = $(this).val()
    getNewSuspectData(timeRange)
  })
})
