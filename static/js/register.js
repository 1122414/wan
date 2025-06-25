// register.js
;(() => {
  ;('use strict')

  const form = document.getElementById('registerForm')
  const validateFields = [
    'username',
    'password',
    'confirmPassword',
    'email',
    'phone',
  ]

  // 初始化验证
  validateFields.forEach((fieldId) => {
    const field = document.getElementById(fieldId)
    field.parentElement.classList.add('position-relative') // 保持定位

    field.addEventListener('blur', validateField)
    field.addEventListener('input', () => validateField({ target: field }))
  })

  function validateField(event) {
    const field = event.target

    // 清除旧状态
    field.classList.remove('is-valid', 'is-invalid')

    // 特殊处理确认密码字段
    if (field.id === 'confirmPassword') {
      const password = document.getElementById('password').value
      if (field.value !== password) {
        field.classList.add('is-invalid')
        return
      }
    }

    // 更新验证状态
    if (field.checkValidity() && field.value.trim()) {
      field.classList.add('is-valid')
    } else if (field.value.trim()) {
      field.classList.add('is-invalid')
    }
  }

  // 密码显示/隐藏功能
  document.querySelectorAll('.password-toggle').forEach((toggle) => {
    toggle.addEventListener('click', function () {
      const input = this.previousElementSibling
      const icon = this.querySelector('i')

      // 切换密码显示/隐藏
      if (input.type === 'password') {
        input.type = 'text'
        icon.classList.remove('bi-eye-slash')
        icon.classList.add('bi-eye')
      } else {
        input.type = 'password'
        icon.classList.remove('bi-eye')
        icon.classList.add('bi-eye-slash')
      }
    })
  })

  // 保留表单提交验证
  form.addEventListener(
    'submit',
    function (event) {
      event.preventDefault()
      event.stopPropagation()

      // 触发全部字段验证
      validateFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId)
        field.dispatchEvent(new Event('blur'))
      })

      // 特别检查确认密码
      const password = document.getElementById('password').value
      const confirmPassword = document.getElementById('confirmPassword').value
      if (password !== confirmPassword) {
        document.getElementById('confirmPassword').classList.add('is-invalid')
        return
      }

      if (form.checkValidity()) {
        this.submit()
      }

      form.classList.add('was-validated')
      form.classList.add('is-invalid')
    },
    false
  )

  // 倒计时功能
  function startCountdown(seconds) {
    const btn = document.getElementById('getCaptchaBtn')
    let remaining = seconds

    const timer = setInterval(() => {
      btn.textContent = `${remaining}秒后重新获取`
      remaining--

      if (remaining < 0) {
        clearInterval(timer)
        btn.disabled = false
        btn.textContent = '获取验证码'
      }
    }, 1000)
  }

  // 发送验证码功能
  function sendCaptcha() {
    const email = document.getElementById('email').value
    const btn = document.getElementById('getCaptchaBtn')
    btn.disabled = true

    fetch(`/auth/captcha/email?email=${email}`)
      .then((response) => response.json())
      .then((data) => {
        console.log(data)
        if (data.code === 200) {
          console.log('验证码发送成功')
          startCountdown(60) //TODO: 别忘记打开
        } else {
          alert(data.msg)
          btn.disabled = false
        }
      })
  }
  window.sendCaptcha = sendCaptcha
})()
