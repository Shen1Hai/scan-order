<template>
  <div class="tables">
    <div class="page-header">
      <h2 class="page-title">桌位管理</h2>
      <div class="header-actions">
        <el-button @click="generateAllQrcodes">生成所有二维码</el-button>
        <el-button type="primary" @click="showDialog('add')">
          <el-icon><Plus /></el-icon> 添加桌位
        </el-button>
      </div>
    </div>

    <el-card>
      <el-table :data="tables" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="桌位名称" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="generateQrcode(row)">
              生成二维码
            </el-button>
            <el-button type="warning" size="small" @click="showDialog('edit', row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="桌位编码" prop="code">
          <el-input v-model="form.code" placeholder="如: T01" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="桌位名称" prop="name">
          <el-input v-model="form.name" placeholder="如: 1号桌" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="idle">空闲</el-radio>
            <el-radio label="occupied">占用</el-radio>
            <el-radio label="reserved">预约</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 二维码预览对话框 -->
    <el-dialog v-model="qrcodeVisible" title="桌位二维码" width="300px">
      <div class="qrcode-container">
        <img v-if="qrcodeData" :src="'data:image/png;base64,' + qrcodeData" alt="二维码" />
        <p class="table-name">{{ currentTable?.name }}</p>
        <p class="table-code">{{ currentTable?.code }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/request'

const tables = ref([])
const dialogVisible = ref(false)
const qrcodeVisible = ref(false)
const dialogTitle = ref('添加桌位')
const formRef = ref()
const isEdit = ref(false)
const editingId = ref(null)
const qrcodeData = ref('')
const currentTable = ref(null)

const statusMap = {
  idle: { text: '空闲', type: 'success' },
  occupied: { text: '占用', type: 'danger' },
  reserved: { text: '预约', type: 'warning' }
}

const getStatusType = (status) => statusMap[status]?.type || ''
const getStatusText = (status) => statusMap[status]?.text || status

const form = ref({
  code: '',
  name: '',
  status: 'idle'
})

const rules = {
  code: [{ required: true, message: '请输入桌位编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入桌位名称', trigger: 'blur' }]
}

const loadTables = async () => {
  try {
    tables.value = await api.getTables()
  } catch (e) {
    ElMessage.error('获取桌位失败')
  }
}

const showDialog = (type, row = null) => {
  if (type === 'add') {
    dialogTitle.value = '添加桌位'
    isEdit.value = false
    form.value = { code: '', name: '', status: 'idle' }
  } else {
    dialogTitle.value = '编辑桌位'
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
        await api.updateTable(editingId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.createTable(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadTables()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该桌位吗?', '提示', { type: 'warning' })
    await api.deleteTable(id)
    ElMessage.success('删除成功')
    loadTables()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const generateQrcode = async (row) => {
  try {
    const res = await api.getTableQrcode(row.id)
    qrcodeData.value = res.qrcode_base64
    currentTable.value = row
    qrcodeVisible.value = true
  } catch (e) {
    ElMessage.error('生成二维码失败')
  }
}

const generateAllQrcodes = async () => {
  try {
    const res = await api.batchGetQrcodes()
    ElMessage.success(`已生成 ${res.length} 个二维码`)
    // TODO: 下载功能
  } catch (e) {
    ElMessage.error('生成二维码失败')
  }
}

onMounted(() => {
  loadTables()
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

.qrcode-container {
  text-align: center;
}

.qrcode-container img {
  width: 200px;
  height: 200px;
  margin-bottom: 16px;
}

.table-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.table-code {
  color: #999;
  font-size: 14px;
}
</style>
