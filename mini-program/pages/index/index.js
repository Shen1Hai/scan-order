// pages/index/index.js
const app = getApp()

Page({
  data: {
    showManualInput: false,
    tableCode: '',
    tableId: null,
    tableName: '',
    tableStatus: '空闲'
  },

  onLoad() {
    // 检查本地存储的桌位信息
    const tableId = wx.getStorageSync('tableId')
    const tableName = wx.getStorageSync('tableName')
    if (tableId) {
      this.setData({
        tableId,
        tableName
      })
    }
  },

  // 扫描二维码
  scanQRCode() {
    wx.scanCode({
      success: res => {
        console.log('扫码结果:', res)
        // 解析二维码内容
        // 格式: scanorder://table/T01
        let tableCode = ''
        if (res.path) {
          const match = res.path.match(/\/table\/([^\/]+)/)
          if (match) {
            tableCode = match[1]
          }
        }
        if (!tableCode && res.result) {
          // 尝试从 result 中提取
          const resultMatch = res.result.match(/table[=:]?([A-Za-z0-9]+)/)
          if (resultMatch) {
            tableCode = resultMatch[1]
          }
        }

        if (tableCode) {
          this.getTableInfo(tableCode)
        } else {
          wx.showToast({
            title: '无效的二维码',
            icon: 'none'
          })
        }
      },
      fail: err => {
        wx.showToast({
          title: '扫码失败',
          icon: 'none'
        })
      }
    })
  },

  // 切换手动输入
  toggleManualInput() {
    this.setData({
      showManualInput: true
    })
  },

  // 桌位码输入
  onTableCodeInput(e) {
    this.setData({
      tableCode: e.detail.value
    })
  },

  // 确认桌位码
  confirmTable() {
    const tableCode = this.data.tableCode.trim()
    if (!tableCode) {
      wx.showToast({
        title: '请输入桌位码',
        icon: 'none'
      })
      return
    }
    this.getTableInfo(tableCode)
  },

  // 获取桌位信息
  async getTableInfo(tableCode) {
    try {
      const res = await app.request(`/api/tables/by-code/${tableCode}`)
      if (res.id) {
        app.setTableInfo(res.id, res.name, res.code)
        this.setData({
          tableId: res.id,
          tableName: res.name,
          tableCode: res.code,
          tableStatus: res.status === 'idle' ? '空闲' : '占用',
          showManualInput: false
        })
        wx.showToast({
          title: '桌位信息已获取',
          icon: 'success'
        })
      }
    } catch (e) {
      wx.showToast({
        title: '桌位不存在',
        icon: 'none'
      })
    }
  },

  // 开始点单
  startOrder() {
    wx.switchTab({
      url: '/pages/menu/menu'
    })
  }
})
