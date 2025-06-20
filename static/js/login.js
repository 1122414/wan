// login.js
;(() => {
  'use strict'

  const form = document.getElementById('loginForm')
  const validateFields = ['username', 'password']

  // 初始化验证
  validateFields.forEach((fieldId) => {
    const field = document.getElementById(fieldId)
    if (field) {
      field.parentElement.classList.add('position-relative') // 保持定位

      field.addEventListener('blur', validateField)
      field.addEventListener('input', () => validateField({ target: field }))
    }
  })

  function validateField(event) {
    const field = event.target

    // 清除旧状态
    field.classList.remove('is-valid', 'is-invalid')

    // 更新验证状态
    if (field.checkValidity() && field.value.trim()) {
      field.classList.add('is-valid')
    } else if (field.value.trim()) {
      field.classList.add('is-invalid')
    }
  }

  // 表单提交验证
  if (form) {
    form.addEventListener(
      'submit',
      function (event) {
        event.preventDefault()
        event.stopPropagation()

        // 先清除可能存在的旧消息
        const oldAlert = document.querySelector('.login-alert')
        if (oldAlert) {
          oldAlert.remove()
        }

        // 触发全部字段验证
        let isValid = true
        validateFields.forEach((fieldId) => {
          const field = document.getElementById(fieldId)
          if (field) {
            field.dispatchEvent(new Event('blur'))
            if (!field.checkValidity() || !field.value.trim()) {
              isValid = false
            }
          }
        })

        if (isValid) {
          if (form.checkValidity()) {
            // 使用AJAX提交表单
            const formData = new FormData(form)

            fetch(form.action, {
              method: 'POST',
              body: formData,
              headers: {
                'X-Requested-With': 'XMLHttpRequest',
              },
            })
              .then((response) => response.json())
              .then((data) => {
                if (data.code === 200) {
                  // 登录成功
                  showMessage('登录成功，正在跳转...', 'success')

                  // 保存记住我的状态
                  const rememberMeCheckbox =
                    document.getElementById('rememberMe')
                  const usernameField = document.getElementById('username')
                  if (
                    rememberMeCheckbox &&
                    rememberMeCheckbox.checked &&
                    usernameField
                  ) {
                    localStorage.setItem(
                      'rememberedUsername',
                      usernameField.value
                    )
                  } else {
                    localStorage.removeItem('rememberedUsername')
                  }

                  // 跳转到主页
                  setTimeout(() => {
                    window.location.href = '/'
                  }, 1500) // 增加延迟时间，确保用户能看到成功消息
                } else {
                  // 登录失败
                  showMessage(
                    data.msg || '登录失败，请检查账号和密码',
                    'danger'
                  )
                }
              })
              .catch((error) => {
                console.error('登录请求出错:', error)
                showMessage('登录请求失败，请稍后重试', 'danger')
              })
          }

          form.classList.add('was-validated')
        }
      },
      false
    )
  }

  // 显示消息提示
  function showMessage(message, type) {
    // 移除旧消息
    const oldAlert = document.querySelector('.login-alert')
    if (oldAlert) {
      oldAlert.remove()
    }

    // 创建新消息
    const alertDiv = document.createElement('div')
    alertDiv.className = `alert alert-${type} login-alert`
    alertDiv.textContent = message

    // 插入到表单前面
    form.parentNode.insertBefore(alertDiv, form)

    // 自动消失
    if (type !== 'success') {
      setTimeout(() => {
        alertDiv.remove()
      }, 5000)
    }
  }

  // 记住我功能
  const rememberMeCheckbox = document.getElementById('rememberMe')
  if (rememberMeCheckbox) {
    // 检查本地存储中是否有保存的用户名
    const savedUsername = localStorage.getItem('rememberedUsername')
    if (savedUsername) {
      const usernameField = document.getElementById('username')
      if (usernameField) {
        usernameField.value = savedUsername
        rememberMeCheckbox.checked = true
      }
    }
  }

  // 密码显示/隐藏切换
  const togglePasswordBtn = document.getElementById('togglePassword')
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', function () {
      const passwordField = document.getElementById('password')
      const icon = this.querySelector('i')

      if (passwordField.type === 'password') {
        passwordField.type = 'text'
        icon.classList.remove('bi-eye')
        icon.classList.add('bi-eye-slash')
      } else {
        passwordField.type = 'password'
        icon.classList.remove('bi-eye-slash')
        icon.classList.add('bi-eye')
      }
    })
  }
})()
