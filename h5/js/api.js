/**
 * H5 顾客端 - API 服务
 */

const API = {
    // 获取桌位信息
    async getTable(code) {
        const res = await fetch(getApiUrl(`/api/tables/by-code/${code}`));
        if (!res.ok) throw new Error('桌位不存在');
        return await res.json();
    },

    // 获取分类列表
    async getCategories() {
        const res = await fetch(getApiUrl('/api/categories?status=active'));
        if (!res.ok) throw new Error('获取分类失败');
        return await res.json();
    },

    // 获取菜品列表
    async getDishes(categoryId = null) {
        let url = '/api/dishes?status=active';
        if (categoryId) {
            url += `&category_id=${categoryId}`;
        }
        const res = await fetch(getApiUrl(url));
        if (!res.ok) throw new Error('获取菜品失败');
        return await res.json();
    },

    // 获取所有菜品（按分类分组）
    async getMenu() {
        const res = await fetch(getApiUrl('/api/dishes?status=active'));
        if (!res.ok) throw new Error('获取菜单失败');
        return await res.json();
    },

    // 创建订单
    async createOrder(orderData) {
        const res = await fetch(getApiUrl('/api/orders'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || '创建订单失败');
        }
        return await res.json();
    },

    // 模拟支付
    async payOrder(orderId) {
        const res = await fetch(getApiUrl(`/api/orders/${orderId}/pay`), {
            method: 'POST'
        });
        if (!res.ok) throw new Error('支付失败');
        return await res.json();
    },

    // 获取订单列表
    async getOrders(tableId) {
        const res = await fetch(getApiUrl(`/api/orders?table_id=${tableId}`));
        if (!res.ok) throw new Error('获取订单失败');
        return await res.json();
    },

    // 获取订单详情
    async getOrder(orderNo) {
        const res = await fetch(getApiUrl(`/api/orders/no/${orderNo}`));
        if (!res.ok) throw new Error('获取订单详情失败');
        return await res.json();
    }
};

// WebSocket 连接
class WebSocketService {
    constructor() {
        this.ws = null;
        this reconnectInterval = 3000;
    }

    connect() {
        try {
            this.ws = new WebSocket(CONFIG.WS_URL);

            this.ws.onopen = () => {
                console.log('WebSocket 已连接');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('WebSocket 消息解析失败:', e);
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket 已断开，正在重连...');
                setTimeout(() => this.connect(), this.reconnectInterval);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
            };
        } catch (e) {
            console.error('WebSocket 连接失败:', e);
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'order_status':
                // 订单状态更新通知
                if (data.data.order_no === STATE.currentOrderNo) {
                    STATE.currentOrderStatus = data.data.status;
                    // 更新订单状态显示
                    this.onOrderStatusChange && this.onOrderStatusChange(data.data);
                }
                break;
            case 'pong':
                // 心跳响应
                break;
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// 全局 WebSocket 实例
const wsService = new WebSocketService();
