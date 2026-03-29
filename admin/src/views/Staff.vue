<template>
  <div class="staff">
    <div class="page-header">
      <h2 class="page-title">员工管理</h2>
      <el-button type="primary" @click="showDialog('add')">
        <el-icon><Plus /></el-icon> 添加员工
      </el-button>
    </div>

    <el-card>
      <el-table :data="staffList" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag>{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showDialog('edit', row)">
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
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="店长" value="manager" />
            <el-option label="收银员" value="cashier" />
            <el-option label="后厨" value="cook" />
            <el-option label="服务员" value="waiter" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/request'

const staffList = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加员工')
const formRef = ref()
const isEdit = ref(false)
const editingId = ref(null)

const roleMap = {
  super_admin: '超级管理员',
  manager: '店长',
  cashier: '收银员',
  cook: '后厨',
  waiter: '服务员'
}

const getRoleText = (role) => roleMap[role] || role

const form = ref({
  username: '',
  name: '',
  password: '',
  role: 'cashier',
  status: 'active'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const loadStaff = async () => {
  try {
    staffList.value = await api.getStaff()
  } catch (e) {
    ElMessage.error('获取员工失败')
  }
}

const showDialog = (type, row = null) => {
  if (type === 'add') {
    dialogTitle.value = '添加员工'
    isEdit.value = false
    form.value = { username: '', name: '', password: '', role: 'cashier', status: 'active' }
  } else {
    dialogTitle.value = '编辑员工'
    isEdit.value = true
    editingId.value = row.id
    form.value = { ...row, password: '' }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEdit.value) {
        const data = { ...form.value }
        if (!data.password) delete data.password
        await api.updateStaff(editingId.value, data)
        ElMessage.success('更新成功')
      } else {
        await api.createStaff(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadStaff()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该员工吗?', '提示', { type: 'warning' })
    await api.deleteStaff(id)
    ElMessage.success('删除成功')
    loadStaff()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadStaff()
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
</style>
