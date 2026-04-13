<template>
  <div class="roles">
    <div class="page-header">
      <h2 class="page-title">角色管理</h2>
      <el-button type="primary" @click="showCreateDialog">新增角色</el-button>
    </div>

    <el-card>
      <el-table :data="roles" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_system" label="系统角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_system ? 'danger' : 'success'" size="small">
              {{ row.is_system ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限数量" width="100">
          <template #default="{ row }">
            <span>{{ row.permissions?.length || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showPermissionsDialog(row)">
              分配权限
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)" :disabled="row.is_system">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增角色对话框 -->
    <el-dialog v-model="createDialogVisible" title="新增角色" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="角色编码" required>
          <el-input v-model="createForm.code" placeholder="如: manager" />
        </el-form-item>
        <el-form-item label="角色名称" required>
          <el-input v-model="createForm.name" placeholder="如: 店长" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" placeholder="角色描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限分配对话框 -->
    <el-dialog v-model="permDialogVisible" title="分配权限" width="700px">
      <div class="permission-grid">
        <div v-for="cat in permissionCategories" :key="cat.name" class="permission-category">
          <h4>{{ cat.label }}</h4>
          <el-checkbox
            v-for="perm in cat.permissions"
            :key="perm.id"
            :model-value="selectedPerms.includes(perm.id)"
            @change="(val) => togglePerm(perm.id, val)"
          >
            {{ perm.name }}
          </el-checkbox>
        </div>
      </div>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/request'

const roles = ref([])
const allPermissions = ref([])
const loading = ref(false)
const permDialogVisible = ref(false)
const currentRole = ref(null)
const selectedPerms = ref([])

// 新增角色
const createDialogVisible = ref(false)
const createLoading = ref(false)
const createForm = ref({
  code: '',
  name: '',
  description: ''
})

const permissionCategories = computed(() => {
  const cats = {}
  allPermissions.value.forEach(perm => {
    if (!cats[perm.category]) {
      cats[perm.category] = { name: perm.category, label: getCategoryLabel(perm.category), permissions: [] }
    }
    cats[perm.category].permissions.push(perm)
  })
  return Object.values(cats)
})

const getCategoryLabel = (cat) => {
  const labels = {
    merchant: '商户',
    category: '分类',
    dish: '菜品',
    table: '桌位',
    order: '订单',
    staff: '员工',
    department: '部门',
    role: '角色',
    inventory: '库存',
    report: '报表',
    coupon: '优惠券',
    system: '系统'
  }
  return labels[cat] || cat
}

const loadRoles = async () => {
  loading.value = true
  try {
    roles.value = await api.getRoles()
  } catch (e) {
    ElMessage.error('获取角色失败')
  } finally {
    loading.value = false
  }
}

const loadPermissions = async () => {
  try {
    allPermissions.value = await api.getAllPermissions()
  } catch (e) {
    ElMessage.error('获取权限列表失败')
  }
}

const showPermissionsDialog = (row) => {
  currentRole.value = row
  selectedPerms.value = (row.permissions || []).map(p => Number(p.id))
  permDialogVisible.value = true
}

const togglePerm = (permId, checked) => {
  if (checked) {
    selectedPerms.value.push(permId)
  } else {
    selectedPerms.value = selectedPerms.value.filter(id => id !== permId)
  }
}

const handleSavePermissions = async () => {
  try {
    await api.updateRolePermissions(currentRole.value.id, {
      permission_ids: selectedPerms.value
    })
    ElMessage.success('权限更新成功')
    permDialogVisible.value = false
    loadRoles()
  } catch (e) {
    ElMessage.error('权限更新失败')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗?', '提示', { type: 'warning' })
    await api.deleteRole(id)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const showCreateDialog = () => {
  createForm.value = { code: '', name: '', description: '' }
  createDialogVisible.value = true
}

const handleCreate = async () => {
  if (!createForm.value.code || !createForm.value.name) {
    ElMessage.warning('请填写角色编码和名称')
    return
  }
  createLoading.value = true
  try {
    await api.createRole(createForm.value)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    loadRoles()
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    createLoading.value = false
  }
}

onMounted(() => {
  loadRoles()
  loadPermissions()
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

.permission-grid {
  max-height: 400px;
  overflow-y: auto;
}

.permission-category {
  margin-bottom: 20px;
}

.permission-category h4 {
  margin-bottom: 10px;
  color: #409eff;
  font-size: 14px;
}

.permission-category :deep(.el-checkbox) {
  margin-left: 20px;
  margin-bottom: 8px;
  width: 120px;
}
</style>
