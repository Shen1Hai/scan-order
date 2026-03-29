// pages/menu/menu.js
const app = getApp()

Page({
  data: {
    categories: [],
    dishes: [],
    currentCategory: '',
    cart: [],
    cartCount: 0,
    cartTotal: '0.00'
  },

  onLoad() {
    this.loadCategories()
    this.loadDishes()
  },

  onShow() {
    // 更新购物车状态
    this.updateCartUI()
  },

  // 加载分类
  async loadCategories() {
    try {
      const res = await app.request('/api/categories?status=active')
      this.setData({
        categories: Array.isArray(res) ? res : []
      })
    } catch (e) {
      console.error('获取分类失败:', e)
    }
  },

  // 加载菜品
  async loadDishes() {
    try {
      const res = await app.request('/api/dishes?status=active')
      const dishes = Array.isArray(res) ? res : []
      // 添加计数属性
      dishes.forEach(dish => {
        dish.count = 0
      })
      this.setData({
        dishes
      })
      this.updateCartUI()
    } catch (e) {
      console.error('获取菜品失败:', e)
    }
  },

  // 选择分类
  selectCategory(e) {
    const categoryId = e.currentTarget.dataset.id
    this.setData({
      currentCategory: categoryId
    })
  },

  // 添加到购物车
  addToCart(e) {
    const dishId = e.currentTarget.dataset.id
    const dish = this.data.dishes.find(d => d.id === dishId)
    if (!dish) return

    const cart = app.getCart()
    const existing = cart.find(item => item.dish_id === dishId)

    if (existing) {
      existing.quantity++
    } else {
      cart.push({
        dish_id: dish.id,
        dish_name: dish.name,
        price: parseFloat(dish.price),
        quantity: 1
      })
    }

    app.updateCart(cart)
    this.updateCartUI()
  },

  // 从购物车减少
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
      this.updateCartUI()
    }
  },

  // 更新购物车 UI
  updateCartUI() {
    const cart = app.getCart()
    let total = 0
    let count = 0

    cart.forEach(item => {
      total += item.price * item.quantity
      count += item.quantity
    })

    // 更新菜品列表中的计数
    const dishes = this.data.dishes.map(dish => {
      const cartItem = cart.find(item => item.dish_id === dish.id)
      return {
        ...dish,
        count: cartItem ? cartItem.quantity : 0
      }
    })

    this.setData({
      cart,
      dishes,
      cartCount: count,
      cartTotal: total.toFixed(2)
    })
  },

  // 跳转到购物车
  goToCart() {
    wx.navigateTo({
      url: '/pages/cart/cart'
    })
  }
})
