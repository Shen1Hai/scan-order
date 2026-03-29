// pages/orders/orders.js
const app = getApp()

Page({
  data: {
    orders: [],
    tableId: null
  },

  onLoad() {
    const tableInfo = app.getTableInfo()
    this.setData({
      tableId: tableInfo.tableId
    })
  },

  onShow() {
    if (this.data.tableId) {
      this.loadOrders()
    }
  },

  async loadOrders() {
    try {
      const res = await app.request(`/api/orders?table_id=${this.data.tableId}`)
      this.setData({
        orders: Array.isArray(res) ? res : []
      })
    } catch (e) {
      console.error('获取订单失败:', e)
    }
  },

  getStatusText(status) {
    const statusMap = {
      'pending': '待支付',
      'paid': '已支付',
      'preparing': '制作中',
      'ready': '待取餐',
      'completed': '已完成',
      'cancelled': '已取消'
    }
    return statusMap[status] || status
  },

  formatTime(time) {
    if (!time) return '-'
    const date = new Date(time)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  }
})
