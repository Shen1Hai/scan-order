<template>
  <div class="dishes">
    <div class="page-header">
      <h2 class="page-title">菜品管理</h2>
      <el-button type="primary" @click="showDialog('add')">
        <el-icon><Plus /></el-icon> 添加菜品
      </el-button>
    </div>

    <el-card>
      <el-table :data="dishes" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="菜品名称" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ parseFloat(row.price).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '上架' : '下架' }}
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="菜品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入菜品名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">上架</el-radio>
            <el-radio label="off_sale">下架</el-radio>
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

const dishes = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加菜品')
const formRef = ref()
const isEdit = ref(false)
const editingId = ref(null)

const form = ref({
  name: '',
  category_id: null,
  price: 0,
  stock: 0,
  description: '',
  status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入菜品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}

const loadDishes = async () => {
  try {
    dishes.value = await api.getDishes()
  } catch (e) {
    ElMessage.error('获取菜品失败')
  }
}

const loadCategories = async () => {
  try {
    categories.value = await api.getCategories()
  } catch (e) {
    console.error('获取分类失败:', e)
  }
}

const showDialog = (type, row = null) => {
  if (type === 'add') {
    dialogTitle.value = '添加菜品'
    isEdit.value = false
    form.value = { name: '', category_id: null, price: 0, stock: 0, description: '', status: 'active' }
  } else {
    dialogTitle.value = '编辑菜品'
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
        await api.updateDish(editingId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await api.createDish(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadDishes()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该菜品吗?', '提示', { type: 'warning' })
    await api.deleteDish(id)
    ElMessage.success('删除成功')
    loadDishes()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadDishes()
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
