document.addEventListener('DOMContentLoaded', function () {
  // 加载热点事件
  function loadHotspotEvents(source = '', page = 1) {
    fetch(`/service/hotspot/events?source=${source}&page=${page}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.code === 200) {
          renderHotspotEvents(data.data, data.pagination, source)
        }
      })
  }

  // 渲染热点事件
  function renderHotspotEvents(events, pagination, source) {
    const container = document.querySelector('.hotspot-list')
    container.innerHTML = ''

    events.forEach((event) => {
      const badgeClass =
        event.threaten_level === '高'
          ? 'bg-danger'
          : event.threaten_level === '中'
          ? 'bg-warning text-dark'
          : 'bg-secondary'

      const itemHTML = `
        <div class="hotspot-item">
          <div class="row">
            <div class="col-md-9">
              <h5 class="hotspot-title">${event.title}</h5>
              <p class="hotspot-desc">${event.content}</p>
              <div class="hotspot-meta">
                <span class="badge ${badgeClass} me-2">${
        event.threaten_level
      }</span>
                <span class="text-muted">
                  <i class="bi bi-calendar3"></i> ${event.insert_time}
                </span>
                <span class="badge bg-info ms-3">
                  ${event.source === 't' ? 'Telegram' : 'Tor'}
                </span>
              </div>
            </div>
            <div class="col-md-3 d-flex align-items-center">
              <button class="btn btn-outline-primary w-100 view-detail" data-id="${
                event.id
              }">
                查看详情
              </button>
            </div>
          </div>
        </div>
        <hr />
      `
      container.insertAdjacentHTML('beforeend', itemHTML)
    })

    // 添加详情按钮事件
    document.querySelectorAll('.view-detail').forEach((btn) => {
      btn.addEventListener('click', function () {
        const id = this.getAttribute('data-id')
        viewEventDetail(id)
      })
    })

    // 更新分页
    updatePagination(pagination, source)
  }

  // 查看详情
  function viewEventDetail(id) {
    // 实际项目中可以跳转到详情页
    alert(`查看事件详情 ID: ${id}`)
  }

  // 更新分页
  function updatePagination(pagination, source) {
    const paginationEl = document.querySelector('.pagination')
    paginationEl.innerHTML = ''

    const currentPage = pagination.current_page
    const totalPages = pagination.total_pages

    // 最多显示10页
    const maxVisiblePages = 10
    let startPage, endPage

    if (totalPages <= maxVisiblePages) {
      startPage = 1
      endPage = totalPages
    } else {
      const maxPagesBeforeCurrent = Math.floor(maxVisiblePages / 2)
      const maxPagesAfterCurrent = Math.ceil(maxVisiblePages / 2) - 1

      if (currentPage <= maxPagesBeforeCurrent) {
        startPage = 1
        endPage = maxVisiblePages
      } else if (currentPage + maxPagesAfterCurrent >= totalPages) {
        startPage = totalPages - maxVisiblePages + 1
        endPage = totalPages
      } else {
        startPage = currentPage - maxPagesBeforeCurrent
        endPage = currentPage + maxPagesAfterCurrent
      }
    }

    // 添加上一页按钮
    const prevItem = document.createElement('li')
    prevItem.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`
    prevItem.innerHTML = `<a class="page-link" href="#" data-page="${
      currentPage - 1
    }">上一页</a>`
    paginationEl.appendChild(prevItem)

    // 添加首页按钮（如果不在第一页）
    if (startPage > 1) {
      const firstPageItem = document.createElement('li')
      firstPageItem.className = 'page-item'
      firstPageItem.innerHTML = `<a class="page-link" href="#" data-page="1">1</a>`
      paginationEl.appendChild(firstPageItem)

      // 添加省略号（如果起始页大于2）
      if (startPage > 2) {
        const ellipsisItem = document.createElement('li')
        ellipsisItem.className = 'page-item disabled'
        ellipsisItem.innerHTML = `<span class="page-link">...</span>`
        paginationEl.appendChild(ellipsisItem)
      }
    }

    // 添加页码按钮
    for (let i = startPage; i <= endPage; i++) {
      const pageItem = document.createElement('li')
      pageItem.className = `page-item ${i === currentPage ? 'active' : ''}`
      pageItem.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`
      paginationEl.appendChild(pageItem)
    }

    // 添加尾页按钮（如果不在最后一页）
    if (endPage < totalPages) {
      // 添加省略号（如果结束页小于总页数-1）
      if (endPage < totalPages - 1) {
        const ellipsisItem = document.createElement('li')
        ellipsisItem.className = 'page-item disabled'
        ellipsisItem.innerHTML = `<span class="page-link">...</span>`
        paginationEl.appendChild(ellipsisItem)
      }

      const lastPageItem = document.createElement('li')
      lastPageItem.className = 'page-item'
      lastPageItem.innerHTML = `<a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>`
      paginationEl.appendChild(lastPageItem)
    }

    // 添加下一页按钮
    const nextItem = document.createElement('li')
    nextItem.className = `page-item ${
      currentPage === totalPages ? 'disabled' : ''
    }`
    nextItem.innerHTML = `<a class="page-link" href="#" data-page="${
      currentPage + 1
    }">下一页</a>`
    paginationEl.appendChild(nextItem)

    // 添加分页事件
    paginationEl.querySelectorAll('.page-link').forEach((link) => {
      link.addEventListener('click', function (e) {
        e.preventDefault()
        const page = parseInt(this.getAttribute('data-page'))
        if (!isNaN(page)) {
          // 调用 performSearch 函数
          performSearch(page, source)
        }
      })
    })

    // 添加分页跳转控件
    addPageJumpControl(pagination, source)
  }

  // 添加分页跳转功能
  function addPageJumpControl(pagination, source) {
    // 移除旧的跳转控件（如果存在）
    const oldJumpContainer = document.querySelector('.page-jump-container')
    if (oldJumpContainer) {
      oldJumpContainer.remove()
    }

    const nav = document.querySelector('nav[aria-label="热点分页"]')
    const jumpContainer = document.createElement('div')
    jumpContainer.className =
      'd-flex align-items-center justify-content-center mt-3 page-jump-container'

    jumpContainer.innerHTML = `
      <span class="me-2">跳至</span>
      <div class="input-group input-group-sm" style="width: 150px;">
        <input type="number" class="form-control" 
               id="pageInput" min="1" max="${pagination.total_pages}" 
               value="${pagination.current_page}">
        <button class="btn btn-outline-secondary" id="goToPageBtn">跳转</button>
      </div>
      <span class="ms-2">页 / 共 ${pagination.total_pages} 页</span>
    `

    nav.parentNode.insertBefore(jumpContainer, nav.nextSibling)

    // 添加跳转事件
    document
      .getElementById('goToPageBtn')
      .addEventListener('click', function () {
        jumpToPage(pagination, source)
      })

    // 添加回车键支持
    document
      .getElementById('pageInput')
      .addEventListener('keyup', function (e) {
        if (e.key === 'Enter') {
          jumpToPage(pagination, source)
        }
      })
  }

  // 执行页面跳转
  function jumpToPage(pagination, source) {
    const pageInput = document.getElementById('pageInput')
    const page = parseInt(pageInput.value)

    if (isNaN(page)) {
      showAlert('请输入有效的页码', 'danger')
      return
    }

    if (page < 1 || page > pagination.total_pages) {
      showAlert(`页码必须在 1 到 ${pagination.total_pages} 之间`, 'danger')
      return
    }

    performSearch(page, source)
  }

  // 执行搜索（加载特定页码的热点事件）
  function performSearch(page = 1, source = '') {
    loadHotspotEvents(source, page)
  }

  // 初始化页面
  loadHotspotEvents()

  // 来源筛选按钮事件
  document.querySelectorAll('.btn-group .btn').forEach((btn) => {
    btn.addEventListener('click', function () {
      // 更新按钮状态
      document
        .querySelectorAll('.btn-group .btn')
        .forEach((b) => b.classList.remove('active'))
      this.classList.add('active')

      // 获取来源类型
      const sourceType = this.textContent.trim()
      let source = ''

      if (sourceType === 'Telegram') source = 't'
      else if (sourceType === 'Tor') source = 'tor'

      // 加载对应来源的事件（重置到第一页）
      performSearch(1, source)
    })
  })

  // 添加词云点击事件处理函数
  function handleWordCloudClick(word) {
    console.log('词云点击:', word)
    window.location.href = `/service/intelligence?keyword=${word}`
  }

  // 初始化页面
  loadHotspotEvents()
})
