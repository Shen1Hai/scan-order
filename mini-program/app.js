/**
 * 扫码点单小程序 - 应用入口
 */
App({
  globalData: {
    // API 配置
    apiBaseUrl: 'http://localhost:8000',

    // 桌位信息
    tableId: null,
    tableName: '',
    tableCode: '',

    // 用户Token
    token: null,

    // 购物车
    cart: []
  },

  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },

  // 更新购物车
  updateCart(cart) {
    this.globalData.cart = cart
    // 同步到本地存储
    wx.setStorageSync('cart', cart)
    // 触发购物车更新事件
    const pages = getCurrentPages()
    if (pages.length > 0) {
      const cartPage = pages.find(p => p.route === 'pages/cart/cart')
      if (cartPage) {
        cartPage.onLoad()
      }
    }
  },

  // 获取购物车
  getCart() {
    return this.globalData.cart || wx.getStorageSync('cart') || []
  },

  // 获取桌位信息
  getTableInfo() {
    return {
      tableId: this.globalData.tableId,
      tableName: this.globalData.tableName,
      tableCode: this.globalData.tableCode
    }
  },

  // 设置桌位信息
  setTableInfo(tableId, tableName, tableCode) {
    this.globalData.tableId = tableId
    this.globalData.tableName = tableName
    this.globalData.tableCode = tableCode
    wx.setStorageSync('tableId', tableId)
    wx.setStorageSync('tableName', tableName)
    wx.setStorageSync('tableCode', tableCode)
  },

  // API 请求封装
  request(url, method = 'GET', data = {}) {
    return new Promise((resolve, reject) => {
      const token = this.globalData.token
      const header = {
        'Content-Type': 'application/json'
      }
      if (token) {
        header['Authorization'] = `Bearer ${token}`
      }

      wx.request({
        url: this.globalData.apiBaseUrl + url,
        method,
        data,
        header,
        success: res => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // token 过期
            wx.removeStorageSync('token')
            this.globalData.token = null
            wx.showToast({
              title: '请重新扫码',
              icon: 'none'
            })
            reject(new Error('Unauthorized'))
          } else {
            wx.showToast({
              title: res.data.detail || '请求失败',
              icon: 'none'
            })
            reject(new Error(res.data.detail))
          }
        },
        fail: err => {
          wx.showToast({
            title: '网络错误',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  }
})
