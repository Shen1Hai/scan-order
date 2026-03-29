/**
 * H5 顾客端 - 主应用
 */

// 状态管理
const STATE = {
    cart: [],           // 购物车
    categories: [],     // 分类列表
    dishes: [],         // 菜品列表
    currentCategory: null,
    tableInfo: null,
    currentOrderNo: null,
    currentOrderStatus: null
};

// DOM 元素
const DOM = {};

// 页面切换
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });
    document.getElementById(pageId).classList.remove('hidden');
}

// Toast 提示
function showToast(message, duration = 2000) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, duration);
}

// 初始化 DOM 引用
function initDOM() {
    DOM.tableName = document.getElementById('table-name');
    DOM.tableStatus = document.getElementById('table-status');
    DOM.categoryTabs = document.getElementById('category-tabs');
    DOM.dishList = document.getElementById('dish-list');
    DOM.cartCount = document.getElementById('cart-count');
    DOM.cartItems = document.getElementById('cart-items');
    DOM.cartTotal = document.getElementById('cart-total');
    DOM.orderSummary = document.getElementById('order-summary');
    DOM.confirmTableName = document.getElementById('confirm-table-name');
    DOM.confirmTotal = document.getElementById('confirm-total');
    DOM.payAmount = document.getElementById('pay-amount');
    DOM.successOrderNo = document.getElementById('success-order-no');
    DOM.ordersList = document.getElementById('orders-list');
}

// 获取分类列表
async function loadCategories() {
    try {
        STATE.categories = await API.getCategories();
        renderCategories();
    } catch (e) {
        showToast(e.message);
    }
}

// 获取菜品列表
async function loadDishes() {
    try {
        STATE.dishes = await API.getMenu();
        renderDishes();
    } catch (e) {
        showToast(e.message);
    }
}

// 渲染分类标签
function renderCategories() {
    if (!STATE.categories.length) return;

    // 添加"全部"分类
    let html = `<div class="category-tab ${!STATE.currentCategory ? 'active' : ''}" data-id="">全部</div>`;

    STATE.categories.forEach(cat => {
        html += `<div class="category-tab ${STATE.currentCategory === cat.id ? 'active' : ''}" data-id="${cat.id}">${cat.name}</div>`;
    });

    DOM.categoryTabs.innerHTML = html;

    // 绑定点击事件
    DOM.categoryTabs.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const categoryId = tab.dataset.id;
            STATE.currentCategory = categoryId ? parseInt(categoryId) : null;
            renderCategories();
            renderDishes();
        });
    });
}

// 渲染菜品列表
function renderDishes() {
    let dishes = STATE.dishes;

    // 按分类筛选
    if (STATE.currentCategory) {
        dishes = dishes.filter(d => d.category_id === STATE.currentCategory);
    }

    if (!dishes.length) {
        DOM.dishList.innerHTML = '<div class="empty-state"><div class="icon">🍽️</div><p>暂无菜品</p></div>';
        return;
    }

    let html = '';
    dishes.forEach(dish => {
        const cartItem = STATE.cart.find(item => item.dish_id === dish.id);
        const count = cartItem ? cartItem.quantity : 0;

        html += `
            <div class="dish-item">
                <div class="dish-image">🍜</div>
                <div class="dish-info">
                    <div class="dish-name">${dish.name}</div>
                    <div class="dish-description">${dish.description || '美味可口'}</div>
                    <div class="dish-bottom">
                        <div class="dish-price">${parseFloat(dish.price).toFixed(2)}</div>
                        <div class="dish-actions">
                            ${count > 0 ? `
                                <button class="btn-minus" data-id="${dish.id}">−</button>
                                <span class="dish-count">${count}</span>
                            ` : ''}
                            <button class="btn-add" data-id="${dish.id}">+</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    DOM.dishList.innerHTML = html;

    // 绑定添加/减少按钮
    DOM.dishList.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', () => addToCart(parseInt(btn.dataset.id)));
    });

    DOM.dishList.querySelectorAll('.btn-minus').forEach(btn => {
        btn.addEventListener('click', () => removeFromCart(parseInt(btn.dataset.id)));
    });
}

// 添加到购物车
function addToCart(dishId) {
    const dish = STATE.dishes.find(d => d.id === dishId);
    if (!dish) return;

    const existing = STATE.cart.find(item => item.dish_id === dishId);
    if (existing) {
        existing.quantity++;
    } else {
        STATE.cart.push({
            dish_id: dish.id,
            dish_name: dish.name,
            price: parseFloat(dish.price),
            quantity: 1
        });
    }

    updateCartCount();
    renderDishes();
}

// 从购物车减少
function removeFromCart(dishId) {
    const existing = STATE.cart.find(item => item.dish_id === dishId);
    if (!existing) return;

    if (existing.quantity > 1) {
        existing.quantity--;
    } else {
        STATE.cart = STATE.cart.filter(item => item.dish_id !== dishId);
    }

    updateCartCount();
    renderDishes();
}

// 更新购物车数量
function updateCartCount() {
    const total = STATE.cart.reduce((sum, item) => sum + item.quantity, 0);
    DOM.cartCount.textContent = total;
    DOM.cartCount.classList.toggle('hidden', total === 0);
}

// 渲染购物车
function renderCart() {
    if (!STATE.cart.length) {
        DOM.cartItems.innerHTML = '<div class="empty-state"><div class="icon">🛒</div><p>购物车是空的</p></div>';
        DOM.cartTotal.textContent = '¥0.00';
        return;
    }

    let html = '';
    let total = 0;

    STATE.cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.dish_name}</div>
                    <div class="cart-item-price">¥${item.price.toFixed(2)} × ${item.quantity}</div>
                </div>
                <div class="cart-item-actions">
                    <button class="btn-minus" data-id="${item.dish_id}">−</button>
                    <span class="dish-count">${item.quantity}</span>
                    <button class="btn-add" data-id="${item.dish_id}">+</button>
                </div>
            </div>
        `;
    });

    DOM.cartItems.innerHTML = html;
    DOM.cartTotal.textContent = `¥${total.toFixed(2)}`;

    // 绑定按钮
    DOM.cartItems.querySelectorAll('.btn-add').forEach(btn => {
        btn.addEventListener('click', () => addToCart(parseInt(btn.dataset.id)));
    });

    DOM.cartItems.querySelectorAll('.btn-minus').forEach(btn => {
        btn.addEventListener('click', () => removeFromCart(parseInt(btn.dataset.id)));
    });
}

// 清空购物车
function clearCart() {
    STATE.cart = [];
    updateCartCount();
    renderCart();
}

// 渲染订单确认页
function renderConfirm() {
    if (!STATE.cart.length) {
        showToast('购物车是空的');
        return;
    }

    let html = '';
    let total = 0;

    STATE.cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        html += `
            <div class="order-summary-item">
                <span>${item.dish_name} × ${item.quantity}</span>
                <span>¥${itemTotal.toFixed(2)}</span>
            </div>
        `;
    });

    DOM.orderSummary.innerHTML = html;
    DOM.confirmTableName.textContent = CONFIG.TABLE_NAME;
    DOM.confirmTotal.textContent = `¥${total.toFixed(2)}`;
}

// 提交订单
async function submitOrder() {
    if (!STATE.cart.length) {
        showToast('购物车是空的');
        return;
    }

    const orderData = {
        table_id: CONFIG.TABLE_ID,
        items: STATE.cart.map(item => ({
            dish_id: item.dish_id,
            dish_name: item.dish_name,
            price: item.price,
            quantity: item.quantity
        }))
    };

    try {
        const order = await API.createOrder(orderData);
        STATE.currentOrderNo = order.order_no;
        showPage('page-pay');
        DOM.payAmount.textContent = `¥${parseFloat(order.total_amount).toFixed(2)}`;
    } catch (e) {
        showToast(e.message);
    }
}

// 确认支付（模拟）
async function confirmPay() {
    if (!STATE.currentOrderNo) return;

    try {
        // 获取订单 ID
        const order = await API.getOrder(STATE.currentOrderNo);
        await API.payOrder(order.id);

        showPage('page-success');
        DOM.successOrderNo.textContent = STATE.currentOrderNo;

        // 清空购物车
        clearCart();
    } catch (e) {
        showToast(e.message);
    }
}

// 加载订单列表
async function loadOrders() {
    if (!CONFIG.TABLE_ID) return;

    try {
        const orders = await API.getOrders(CONFIG.TABLE_ID);
        renderOrders(orders);
    } catch (e) {
        showToast(e.message);
    }
}

// 渲染订单列表
function renderOrders(orders) {
    if (!orders.length) {
        DOM.ordersList.innerHTML = '<div class="empty-state"><div class="icon">📋</div><p>暂无订单</p></div>';
        return;
    }

    let html = '';

    orders.slice(0, 10).forEach(order => {
        const statusMap = {
            'pending': { text: '待支付', class: 'pending' },
            'paid': { text: '已支付', class: 'paid' },
            'preparing': { text: '制作中', class: 'preparing' },
            'ready': { text: '待取餐', class: 'ready' },
            'completed': { text: '已完成', class: 'completed' },
            'cancelled': { text: '已取消', class: 'cancelled' }
        };

        const status = statusMap[order.status] || { text: order.status, class: '' };

        html += `
            <div class="order-card">
                <div class="order-card-header">
                    <span class="order-no">${order.order_no}</span>
                    <span class="order-status ${status.class}">${status.text}</span>
                </div>
                <div class="order-card-total">
                    合计: <span>¥${parseFloat(order.total_amount).toFixed(2)}</span>
                </div>
            </div>
        `;
    });

    DOM.ordersList.innerHTML = html;
}

// 初始化页面
async function initPage() {
    // 解析 URL 中的桌位编码
    parseTableCode();

    // 如果没有桌位编码，显示提示
    if (!CONFIG.TABLE_CODE) {
        DOM.tableName.textContent = '请扫描桌上二维码';
        DOM.tableStatus.textContent = '无法获取桌位';
        return;
    }

    try {
        // 获取桌位信息
        const table = await API.getTable(CONFIG.TABLE_CODE);
        CONFIG.TABLE_ID = table.id;
        CONFIG.TABLE_NAME = table.name;

        DOM.tableName.textContent = table.name;
        DOM.tableStatus.textContent = table.status === 'idle' ? '空闲' : '占用';

        // 连接 WebSocket
        wsService.connect();
    } catch (e) {
        DOM.tableName.textContent = '桌位不存在';
        DOM.tableStatus.textContent = '请重新扫描';
    }
}

// 绑定事件
function bindEvents() {
    // 开始点单
    document.getElementById('btn-start-order').addEventListener('click', async () => {
        if (!CONFIG.TABLE_ID) {
            showToast('请扫描正确的二维码');
            return;
        }
        await loadCategories();
        await loadDishes();
        showPage('page-menu');
    });

    // 返回按钮
    document.getElementById('btn-back-menu').addEventListener('click', () => {
        showPage('page-home');
    });

    // 购物车图标
    document.getElementById('cart-icon').addEventListener('click', () => {
        renderCart();
        showPage('page-cart');
    });

    // 返回购物车
    document.getElementById('btn-back-cart').addEventListener('click', () => {
        showPage('page-menu');
    });

    // 清空购物车
    document.getElementById('btn-clear-cart').addEventListener('click', clearCart);

    // 提交订单
    document.getElementById('btn-submit-order').addEventListener('click', () => {
        renderConfirm();
        showPage('page-confirm');
    });

    // 返回确认页
    document.getElementById('btn-back-confirm').addEventListener('click', () => {
        showPage('page-cart');
    });

    // 支付按钮
    document.getElementById('btn-pay').addEventListener('click', submitOrder);

    // 确认支付
    document.getElementById('btn-confirm-pay').addEventListener('click', confirmPay);

    // 查看订单
    document.getElementById('btn-view-orders').addEventListener('click', async () => {
        await loadOrders();
        showPage('page-orders');
    });

    // 返回订单列表
    document.getElementById('btn-back-orders').addEventListener('click', () => {
        showPage('page-home');
    });

    // 继续点单
    document.getElementById('btn-continue-order').addEventListener('click', () => {
        STATE.currentOrderNo = null;
        showPage('page-home');
    });
}

// 启动应用
document.addEventListener('DOMContentLoaded', async () => {
    initDOM();
    bindEvents();
    await initPage();
});
