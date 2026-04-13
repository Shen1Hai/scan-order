<template>
  <div class="department-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <el-button type="primary" @click="showDialog('create')" v-if="hasPermission('department:write')">
            新增部门
          </el-button>
        </div>
      </template>

      <!-- 部门树 -->
      <el-tree
        :data="departmentTree"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        class="department-tree"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span class="node-info">
              <el-icon v-if="data.status === 'inactive'"><Lock /></el-icon>
              <span>{{ node.label }}</span>
              <el-tag size="small" type="info" v-if="data.status === 'inactive'">停用</el-tag>
            </span>
            <span class="node-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="showDialog('edit', data)"
                v-if="hasPermission('department:write')"
              >
                编辑
              </el-button>
              <el-button
                type="success"
                link
                size="small"
                @click="showSetManager(data)"
                v-if="hasPermission('department:write')"
              >
                设置负责人
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(data)"
                v-if="hasPermission('department:write') && !data.children?.length"
              >
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新增部门' : '编辑部门'"
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="部门名称">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码">
          <el-input v-model="form.code" placeholder="请输入部门编码" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="form.parent_id"
            :data="treeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            check-strictly
            placeholder="请选择上级部门（不选则为顶级）"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 设置负责人对话框 -->
    <el-dialog v-model="managerDialogVisible" title="设置部门负责人" width="400px">
      <el-form label-width="80px">
        <el-form-item label="部门">
          <span>{{ selectedDepartment?.name }}</span>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="managerId" placeholder="请选择负责人" style="width: 100%">
            <el-option
              v-for="staff in staffList"
              :key="staff.id"
              :label="staff.name"
              :value="staff.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="managerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSetManager">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api/request'

const departmentTree = ref([])
const staffList = ref([])
const permissions = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogType = ref('create')
const dialogLoading = ref(false)

// 表单
const form = ref({
  name: '',
  code: '',
  parent_id: null,
  sort_order: 0,
  status: 'active'
})
const editingId = ref(null)

// 负责人
const managerDialogVisible = ref(false)
const selectedDepartment = ref(null)
const managerId = ref(null)

// 权限检查
const hasPermission = (perm) => {
  return permissions.value.includes(perm) || permissions.value.includes('*')
}

// 获取部门树
const loadDepartments = async () => {
  try {
    const data = await api.getDepartmentTree()
    departmentTree.value = data || []
  } catch (e) {
    console.error('加载部门失败:', e)
  }
}

// 获取员工列表
const loadStaff = async () => {
  try {
    const data = await api.getStaff()
    staffList.value = data || []
  } catch (e) {
    console.error('加载员工失败:', e)
  }
}

// 获取权限
const loadPermissions = async () => {
  try {
    const data = await api.getPermissions()
    permissions.value = data.permissions || []
  } catch (e) {
    console.error('加载权限失败:', e)
  }
}

// Tree data for select (excludes current editing node)
const treeData = computed(() => {
  if (!editingId.value) return departmentTree.value
  return filterTree(departmentTree.value, editingId.value)
})

const filterTree = (nodes, excludeId) => {
  return nodes
    .filter(n => n.id !== excludeId)
    .map(n => ({
      ...n,
      children: n.children ? filterTree(n.children, excludeId) : undefined
    }))
}

// 显示对话框
const showDialog = (type, data = null) => {
  dialogType.value = type
  if (type === 'edit' && data) {
    editingId.value = data.id
    form.value = {
      name: data.name,
      code: data.code,
      parent_id: data.parent_id,
      sort_order: data.sort_order || 0,
      status: data.status
    }
  } else {
    editingId.value = null
    form.value = {
      name: '',
      code: '',
      parent_id: null,
      sort_order: 0,
      status: 'active'
    }
  }
  dialogVisible.value = true
}

// 显示设置负责人
const showSetManager = (data) => {
  selectedDepartment.value = data
  managerId.value = data.manager_id || null
  managerDialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!form.value.name || !form.value.code) {
    ElMessage.warning('请填写部门名称和编码')
    return
  }

  dialogLoading.value = true
  try {
    if (dialogType.value === 'create') {
      await api.createDepartment(form.value)
      ElMessage.success('创建成功')
    } else {
      await api.updateDepartment(editingId.value, form.value)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    await loadDepartments()
  } catch (e) {
    console.error('保存失败:', e)
  } finally {
    dialogLoading.value = false
  }
}

// 设置负责人
const handleSetManager = async () => {
  try {
    await api.setDepartmentManager(selectedDepartment.value.id, managerId.value)
    ElMessage.success('设置成功')
    managerDialogVisible.value = false
    await loadDepartments()
  } catch (e) {
    console.error('设置失败:', e)
  }
}

// 删除
const handleDelete = async (data) => {
  try {
    await ElMessageBox.confirm(`确定删除部门"${data.name}"吗？`, '提示', {
      type: 'warning'
    })
    await api.deleteDepartment(data.id)
    ElMessage.success('删除成功')
    await loadDepartments()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
    }
  }
}

onMounted(() => {
  loadDepartments()
  loadStaff()
  loadPermissions()
})
</script>

<style scoped>
.department-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.department-tree {
  width: 100%;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-actions {
  display: flex;
  gap: 8px;
}
</style>
