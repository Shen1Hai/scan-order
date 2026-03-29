// pages/cart/cart.js
const app = getApp()

Page({
  data: {
    cart: [],
    total: '0.00',
    tableId: null,
    tableName: ''
  },

  onLoad() {
    const tableInfo = app.getTableInfo()
    this.setData({
      tableId: tableInfo.tableId,
      tableName: tableInfo.tableName
    })
  },

  onShow() {
    this.loadCart()
  },

  loadCart() {
    const cart = app.getCart()
    let total = 0
    cart.forEach(item => {
      total += item.price * item.quantity
    })
    this.setData({
      cart,
      total: total.toFixed(2)
    })
  },

  addToCart(e) {
    const dishId = e.currentTarget.dataset.id
    const cart = app.getCart()
    const existing = cart.find(item => item.dish_id === dishId)

    if (existing) {
      existing.quantity++
      app.updateCart(cart)
      this.loadCart()
    }
  },

  removeFromCart(e) {
    const dishId = e.currentTarget.dataset.id
    const cart = app.getCart()
    const existing = cart.find(item => item.dish_id === dishId)

    if (existing) {
      if (existing.quantity > 1) {
        existing.quantity--
      } else {
        const index = cart.findIndex(item => item.dish_id === dishId)
        cart.splice(index, 1)
      }
      app.updateCart(cart)
      this.loadCart()
    }
  },

  goToMenu() {
    wx.switchTab({
      url: '/pages/menu/menu'
    })
  },

  async submitOrder() {
    if (!this.data.tableId) {
      wx.showToast({
        title: '请先扫描桌位码',
        icon: 'none'
      })
      return
    }

    if (!this.data.cart.length) {
      wx.showToast({
        title: '购物车是空的',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '提交中...'
    })

    try {
      const orderData = {
        table_id: this.data.tableId,
        items: this.data.cart.map(item => ({
          dish_id: item.dish_id,
          dish_name: item.dish_name,
          price: item.price,
          quantity: item.quantity
        }))
      }

      const res = await app.request('/api/orders', 'POST', orderData)

      // 模拟支付
      await app.request(`/api/orders/${res.id}/pay`, 'POST')

      // 清空购物车
      app.updateCart([])

      wx.hideLoading()
      wx.showToast({
        title: '支付成功',
        icon: 'success'
      })

      // 跳转到订单页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/orders/orders'
        })
      }, 1500)
    } catch (e) {
      wx.hideLoading()
      console.error('提交订单失败:', e)
    }
  }
})
