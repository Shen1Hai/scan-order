<template>
  <div class="orders">
    <div class="page-header">
      <h2 class="page-title">订单管理</h2>
      <div class="header-filters">
        <el-select v-model="filterStatus" placeholder="订单状态" clearable @change="loadOrders">
          <el-option label="全部" value="" />
          <el-option label="待支付" value="pending" />
          <el-option label="已支付" value="paid" />
          <el-option label="制作中" value="preparing" />
          <el-option label="待取餐" value="ready" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </div>
    </div>

    <el-card>
      <el-table :data="orders" stripe v-loading="loading">
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="table_name" label="桌号" width="100" />
        <el-table-column prop="total_amount" label="金额" width="120">
          <template #default="{ row }">
            ¥{{ parseFloat(row.total_amount).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showDetail(row)">
              详情
            </el-button>
            <el-dropdown v-if="row.status === 'pending'" @command="(cmd) => handleCommand(cmd, row)">
              <el-button type="warning" size="small">
                操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="pay">确认支付</el-dropdown-item>
                  <el-dropdown-item command="cancel">取消订单</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-dropdown v-else-if="row.status === 'paid'" @command="(cmd) => handleCommand(cmd, row)">
              <el-button type="primary" size="small">
                操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="preparing">开始制作</el-dropdown-item>
                  <el-dropdown-item command="cancel">取消订单</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button
              v-if="row.status === 'preparing'"
              type="success"
              size="small"
              @click="handleCommand('ready', row)"
            >
              完成制作
            </el-button>
            <el-button
              v-if="row.status === 'ready'"
              type="success"
              size="small"
              @click="handleCommand('completed', row)"
            >
              完成取餐
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > 0"
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="500px">
      <div class="order-detail" v-if="currentOrder">
        <div class="detail-header">
          <p><strong>订单号:</strong> {{ currentOrder.order_no }}</p>
          <p><strong>桌号:</strong> {{ currentOrder.table_name }}</p>
          <p><strong>状态:</strong>
            <el-tag :type="getStatusType(currentOrder.status)" size="small">
              {{ getStatusText(currentOrder.status) }}
            </el-tag>
          </p>
          <p><strong>下单时间:</strong> {{ formatTime(currentOrder.created_at) }}</p>
        </div>
        <el-divider />
        <div class="detail-items">
          <h4>订单项</h4>
          <div v-for="item in currentOrder.items" :key="item.id" class="order-item">
            <span>{{ item.dish_name }} × {{ item.quantity }}</span>
            <span>¥{{ (parseFloat(item.price) * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        <el-divider />
        <div class="detail-total">
          <span>合计:</span>
          <span class="total-amount">¥{{ parseFloat(currentOrder.total_amount).toFixed(2) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/request'

const orders = ref([])
const loading = ref(false)
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailVisible = ref(false)
const currentOrder = ref(null)

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

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    const res = await api.getOrders(params)
    orders.value = Array.isArray(res) ? res : []
    total.value = orders.value.length
  } catch (e) {
    ElMessage.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadOrders()
}

const showDetail = async (row) => {
  try {
    currentOrder.value = await api.getOrder(row.id)
    detailVisible.value = true
  } catch (e) {
    ElMessage.error('获取订单详情失败')
  }
}

const handleCommand = async (command, row) => {
  try {
    switch (command) {
      case 'pay':
        await api.updateOrderStatus(row.id, { status: 'paid' })
        ElMessage.success('已确认支付')
        break
      case 'preparing':
        await api.updateOrderStatus(row.id, { status: 'preparing' })
        ElMessage.success('已开始制作')
        break
      case 'ready':
        await api.updateOrderStatus(row.id, { status: 'ready' })
        ElMessage.success('制作完成')
        break
      case 'completed':
        await api.updateOrderStatus(row.id, { status: 'completed' })
        ElMessage.success('已完成')
        break
      case 'cancel':
        await api.cancelOrder(row.id)
        ElMessage.success('已取消')
        break
    }
    loadOrders()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.order-detail {
  padding: 10px 0;
}

.detail-header p {
  margin-bottom: 8px;
}

.detail-items h4 {
  margin-bottom: 12px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}

.detail-total {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
}

.total-amount {
  color: #f56c6c;
  font-weight: 600;
}
</style>
