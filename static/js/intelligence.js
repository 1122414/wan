// intelligence.js
document.addEventListener('DOMContentLoaded', function () {
  const searchForm = document.querySelector('.intelligence-search-form')
  const searchInput = searchForm.querySelector('input[type="text"]')
  const typeSelect = searchForm.querySelector('#category_select')
  const timeSelect = searchForm.querySelector('#time_select')
  const searchBtn = searchForm.querySelector('button[type="submit"]')

  // 监听搜索表单提交
  searchForm.addEventListener('submit', function (e) {
    e.preventDefault()
    performSearch(1)
  })

  // 搜索函数
  function performSearch(page = 1) {
    const searchParams = {
      keyword: searchInput.value,
      type: typeSelect.value,
      time_range: timeSelect.value,
      page: page,
    }

    console.log(searchParams.type)
    // 显示加载状态
    searchBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status"></span> 搜索中...'
    searchBtn.disabled = true

    // 发送搜索请求
    fetch('/service/intelligence/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(searchParams),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.code === 200) {
          updateIntelligenceTable(data.data, data.pagination)
        } else {
          showAlert('搜索失败: ' + data.msg, 'danger')
        }
      })
      .catch((error) => {
        console.error('搜索出错:', error)
        showAlert('搜索请求失败，请稍后重试', 'danger')
      })
      .finally(() => {
        // 恢复按钮状态
        searchBtn.innerHTML = '<i class="bi bi-search"></i> 搜索'
        searchBtn.disabled = false
      })
  }

  function showContentModal(content) {
    const modalHtml = `
        <div class="modal fade" id="contentModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">情报内容详情</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>${content}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>
    `

    // 移除旧模态框（如果存在）
    const oldModal = document.getElementById('contentModal')
    if (oldModal) oldModal.remove()

    // 添加新模态框并显示
    document.body.insertAdjacentHTML('beforeend', modalHtml)
    const modal = new bootstrap.Modal(document.getElementById('contentModal'))
    modal.show()
  }

  // 更新情报表格
  function updateIntelligenceTable(data, pagination) {
    console.log('98' + pagination)
    const tableBody = document.querySelector('.table tbody')
    tableBody.innerHTML = '' // 清空现有内容

    if (data.length === 0) {
      tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center py-4">未找到匹配的情报</td>
                </tr>
            `
      return
    }

    data.forEach((item) => {
      const row = document.createElement('tr')
      // 风险等级徽章样式
      let badgeClass = 'bg-secondary'
      if (item.threaten_level === '高') badgeClass = 'bg-danger'
      if (item.threaten_level === '中') badgeClass = 'bg-warning text-dark'

      // 创建内容单元格
      const contentCell = document.createElement('td')
      contentCell.className = 'text-truncate'
      contentCell.style.maxWidth = '250px'
      contentCell.style.cursor = 'pointer'
      contentCell.textContent = item.content

      // 添加点击事件监听器（解决作用域问题）
      contentCell.addEventListener('click', () => {
        showContentModal(item.content)
      })

      row.innerHTML = `
        <td>${item.id}</td>
        <td>${item.insert_time}</td>
        <td>${item.label_name}</td>
        <td>${item.user_name}</td>
        <td>${item.area}</td>
        <td><span class="badge ${badgeClass}">${item.threaten_level}</span></td>
      `

      // 将内容单元格插入到正确位置（第二列）
      row.insertBefore(contentCell, row.children[1])

      tableBody.appendChild(row)
    })

    // 添加详情按钮事件
    document.querySelectorAll('.view-detail').forEach((btn) => {
      btn.addEventListener('click', function () {
        const intelId = this.getAttribute('data-id')
        viewIntelligenceDetail(intelId)
      })
    })
    // 更新分页控件
    updatePagination(pagination)
  }

  // 查看详情
  function viewIntelligenceDetail(id) {
    // 这里可以跳转到详情页或显示模态框
    console.log('查看情报详情:', id)
    // 示例: window.location.href = `/service/intelligence/detail/${id}`;
  }

  // 显示消息提示
  function showAlert(message, type) {
    const alertDiv = document.createElement('div')
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`
    alertDiv.role = 'alert'
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `

    const container = document.querySelector('.intelligence-container')
    container.insertBefore(alertDiv, container.firstChild)
  }

  // 分页控件更新函数
  function updatePagination(pagination) {
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
          performSearch(page)
        }
      })
    })

    // 添加分页跳转控件
    addPageJumpControl(pagination)
  }

  // 添加分页跳转功能
  function addPageJumpControl(pagination) {
    // 移除旧的跳转控件（如果存在）
    const oldJumpContainer = document.querySelector('.page-jump-container')
    if (oldJumpContainer) {
      oldJumpContainer.remove()
    }

    const nav = document.querySelector('nav[aria-label="情报分页"]')
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
        jumpToPage(pagination)
      })

    // 添加回车键支持
    document
      .getElementById('pageInput')
      .addEventListener('keyup', function (e) {
        if (e.key === 'Enter') {
          jumpToPage(pagination)
        }
      })
  }

  // 执行页面跳转
  function jumpToPage(pagination) {
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

    performSearch(page)
  }

  // 检查URL中的keyword参数（适配热点分析图云跳转）
  const urlParams = new URLSearchParams(window.location.search)
  const keyword = urlParams.get('keyword')

  if (keyword) {
    // 自动填充搜索框
    searchInput.value = keyword

    // 自动触发搜索（延迟确保DOM加载完成）
    setTimeout(() => {
      performSearch(1)
    }, 300)
  }
})
