<template>
  <div class="inventory">
    <div class="page-header">
      <h2 class="page-title">库存管理</h2>
      <div class="header-actions">
        <el-button @click="showLogDialog">出入库记录</el-button>
        <el-button type="primary" @click="showDialog('add')">
          <el-icon><Plus /></el-icon> 添加物品
        </el-button>
      </div>
    </div>

    <el-card>
      <el-table :data="inventory" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="物品名称" />
        <el-table-column prop="quantity" label="库存数量" width="120">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.is_low_stock }">
              {{ row.quantity }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="low_stock_threshold" label="预警阈值" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_low_stock" type="danger">库存不足</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="showStockDialog('in', row)">
              入库
            </el-button>
            <el-button type="warning" size="small" @click="showStockDialog('out', row)">
              出库
            </el-button>
            <el-button type="primary" size="small" @click="showDialog('edit', row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="物品名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如: 斤、个、箱" />
        </el-form-item>
        <el-form-item label="库存数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0" />
        </el-form-item>
        <el-form-item label="预警阈值" prop="low_stock_threshold">
          <el-input-number v-model="form.low_stock_threshold" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 出入库对话框 -->
    <el-dialog v-model="stockDialogVisible" :title="stockDialogTitle" width="400px">
      <el-form ref="stockFormRef" :model="stockForm" :rules="stockRules" label-width="80px">
        <el-form-item label="物品名称">
          <span>{{ currentItem?.name }}</span>
        </el-form-item>
        <el-form-item label="当前库存">
          <span>{{ currentItem?.quantity }} {{ currentItem?.unit }}</span>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="stockForm.quantity" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="备注" prop="note">
          <el-input v-model="stockForm.note" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStockSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api/request'

const inventory = ref([])
const dialogVisible = ref(false)
const stockDialogVisible = ref(false)
const dialogTitle = ref('添加物品')
const stockDialogTitle = ref('入库')
const formRef = ref()
const stockFormRef = ref()
const isEdit = ref(false)
const editingId = ref(null)
const stockType = ref('in')
const currentItem = ref(null)

const form = ref({
  name: '',
  unit: '个',
  quantity: 0,
  low_stock_threshold: 10
})

const stockForm = ref({
  quantity: 1,
  note: ''
})

const rules = {
  name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }]
}

const stockRules = {
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const loadInventory = async () => {
  try {
    inventory.value = await api.getInventory()
  } catch (e) {
    ElMessage.error('获取库存失败')
  }
}

const showDialog = (type, row = null) => {
  if (type === 'add') {
    dialogTitle.value = '添加物品'
    isEdit.value = false
    form.value = { name: '', unit: '个', quantity: 0, low_stock_threshold: 10 }
  } else {
    dialogTitle.value = '编辑物品'
    isEdit.value = true
    editingId.value = row.id
    form.value = { ...row }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEdit.value) {
        await api.updateInventory(editingId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.createInventory(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadInventory()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const showStockDialog = (type, row) => {
  stockType.value = type
  currentItem.value = row
  stockDialogTitle.value = type === 'in' ? '入库' : '出库'
  stockForm.value = { quantity: 1, note: '' }
  stockDialogVisible.value = true
}

const handleStockSubmit = async () => {
  if (!stockFormRef.value) return
  await stockFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await api.createInventoryLog(currentItem.value.id, {
        type: stockType.value,
        quantity: stockForm.value.quantity,
        note: stockForm.value.note
      })
      ElMessage.success(stockType.value === 'in' ? '入库成功' : '出库成功')
      stockDialogVisible.value = false
      loadInventory()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

onMounted(() => {
  loadInventory()
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

.header-actions {
  display: flex;
  gap: 10px;
}

.low-stock {
  color: #f56c6c;
  font-weight: 600;
}
</style>
