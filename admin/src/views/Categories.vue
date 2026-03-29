<template>
  <div class="categories">
    <div class="page-header">
      <h2 class="page-title">分类管理</h2>
      <el-button type="primary" @click="showDialog('add')">
        <el-icon><Plus /></el-icon> 添加分类
      </el-button>
    </div>

    <el-card>
      <el-table :data="categories" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="sort_order" label="排序" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
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
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/request'

const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加分类')
const formRef = ref()
const isEdit = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  sort_order: 0,
  status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const loadCategories = async () => {
  try {
    categories.value = await api.getCategories()
  } catch (e) {
    ElMessage.error('获取分类失败')
  }
}

const showDialog = (type, row = null) => {
  if (type === 'add') {
    dialogTitle.value = '添加分类'
    isEdit.value = false
    form.value = { name: '', sort_order: 0, status: 'active' }
  } else {
    dialogTitle.value = '编辑分类'
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
        await api.updateCategory(editingId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.createCategory(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadCategories()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该分类吗?', '提示', {
      type: 'warning'
    })
    await api.deleteCategory(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadCategories()
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
