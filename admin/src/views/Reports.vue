<template>
  <div class="reports">
    <h2 class="page-title">报表统计</h2>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>销售统计</span>
              <div class="date-filters">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="loadSalesReport"
                />
              </div>
            </div>
          </template>
          <el-row :gutter="20" class="summary-cards">
            <el-col :span="6">
              <div class="summary-card">
                <p class="label">总销售额</p>
                <p class="value">¥{{ salesReport.total_sales?.toFixed(2) || '0.00' }}</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <p class="label">订单数</p>
                <p class="value">{{ salesReport.order_count || 0 }}</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <p class="label">完成订单</p>
                <p class="value">{{ salesReport.completed_count || 0 }}</p>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-card">
                <p class="label">取消订单</p>
                <p class="value">{{ salesReport.cancelled_count || 0 }}</p>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>菜品销量排行</span>
          </template>
          <el-table :data="dishSales" stripe>
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="dish_name" label="菜品名称" />
            <el-table-column prop="total_quantity" label="销量" align="center" />
            <el-table-column prop="total_amount" label="销售额" align="center">
              <template #default="{ row }">
                ¥{{ row.total_amount?.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>每日销售趋势</span>
          </template>
          <div class="sales-trend">
            <p class="empty-tip">图表展示区域（需要 ECharts）</p>
            <ul>
              <li v-for="item in salesReport.daily_sales" :key="item.date">
                {{ item.date }}: ¥{{ item.amount?.toFixed(2) }} ({{ item.count }} 单)
              </li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/request'

const dateRange = ref([])
const salesReport = ref({})
const dishSales = ref([])

const loadSalesReport = async () => {
  try {
    const params = {}
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    salesReport.value = await api.getSalesReport(params)
  } catch (e) {
    ElMessage.error('获取销售报表失败')
  }
}

const loadDishSales = async () => {
  try {
    const params = {}
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      params.end_date = dateRange.value[1].toISOString().split('T')[0]
    }
    const res = await api.getDishSalesReport(params)
    dishSales.value = res.dishes || []
  } catch (e) {
    console.error('获取菜品报表失败:', e)
  }
}

onMounted(() => {
  // 默认加载最近30天
  const now = new Date()
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  dateRange.value = [thirtyDaysAgo, now]

  loadSalesReport()
  loadDishSales()
})
</script>

<style scoped>
.page-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-cards {
  margin-top: 20px;
}

.summary-card {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-card .label {
  color: #999;
  font-size: 14px;
  margin-bottom: 8px;
}

.summary-card .value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.sales-trend {
  min-height: 200px;
}

.sales-trend ul {
  list-style: none;
  padding: 0;
}

.sales-trend li {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.empty-tip {
  color: #999;
  text-align: center;
  padding: 40px 0;
}
</style>
