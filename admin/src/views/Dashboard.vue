<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">今日销售额</p>
            <p class="stat-value">¥{{ dashboard.today_sales?.toFixed(2) || '0.00' }}</p>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">今日订单</p>
            <p class="stat-value">{{ dashboard.today_orders || 0 }}</p>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">待处理订单</p>
            <p class="stat-value">{{ dashboard.pending_orders || 0 }}</p>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon><Food /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">菜品总数</p>
            <p class="stat-value">{{ totalDishes }}</p>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 畅销菜品 -->
    <el-card class="top-dishes-card">
      <template #header>
        <span>今日畅销菜品</span>
      </template>
      <el-table :data="dashboard.top_dishes || []" stripe>
        <el-table-column prop="name" label="菜品名称" />
        <el-table-column prop="quantity" label="销量" align="center" />
      </el-table>
      <el-empty v-if="!dashboard.top_dishes?.length" description="暂无数据" />
    </el-card>

    <!-- 待处理订单 -->
    <el-card class="pending-orders-card">
      <template #header>
        <div class="card-header">
          <span>待处理订单</span>
          <el-button type="primary" size="small" @click="$router.push('/orders')">
            查看全部
          </el-button>
        </div>
      </template>
      <el-table :data="pendingOrders" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="table_name" label="桌号" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'paid'"
              type="primary"
              size="small"
              @click="handleUpdateStatus(row, 'preparing')"
            >
              开始制作
            </el-button>
            <el-button
              v-if="row.status === 'preparing'"
              type="success"
              size="small"
              @click="handleUpdateStatus(row, 'ready')"
            >
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!pendingOrders.length" description="暂无待处理订单" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api/request'
import { ElMessage } from 'element-plus'

const dashboard = ref({})
const pendingOrders = ref([])
const totalDishes = ref(0)

const statusMap = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'info' },
  preparing: { text: '制作中', type: '' },
  ready: { text: '待取餐', type: 'success' },
  completed: { text: '已完成', type: 'info' },
  cancelled: { text: '已取消', type: 'danger' }
}

const getStatusType = (status) => statusMap[status]?.type || ''
const getStatusText = (status) => statusMap[status]?.text || status

const loadDashboard = async () => {
  try {
    dashboard.value = await api.getDashboard()
  } catch (e) {
    console.error('获取仪表盘数据失败:', e)
  }
}

const loadPendingOrders = async () => {
  try {
    const orders = await api.getOrders({ status: 'paid,preparing' })
    pendingOrders.value = Array.isArray(orders) ? orders.slice(0, 5) : []
  } catch (e) {
    console.error('获取待处理订单失败:', e)
  }
}

const loadDishes = async () => {
  try {
    const dishes = await api.getDishes()
    totalDishes.value = Array.isArray(dishes) ? dishes.length : 0
  } catch (e) {
    console.error('获取菜品数量失败:', e)
  }
}

const handleUpdateStatus = async (order, status) => {
  try {
    await api.updateOrderStatus(order.id, { status })
    ElMessage.success('更新成功')
    loadPendingOrders()
    loadDashboard()
  } catch (e) {
    console.error('更新订单状态失败:', e)
  }
}

onMounted(() => {
  loadDashboard()
  loadPendingOrders()
  loadDishes()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-title {
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  color: #999;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.top-dishes-card,
.pending-orders-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
