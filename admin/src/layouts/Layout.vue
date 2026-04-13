<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h3>扫码点单</h3>
        <p>管理后台</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/categories" v-if="hasPermission('category:read')">
          <el-icon><Grid /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/dishes" v-if="hasPermission('dish:read')">
          <el-icon><Food /></el-icon>
          <span>菜品管理</span>
        </el-menu-item>
        <el-menu-item index="/tables" v-if="hasPermission('table:read')">
          <el-icon><Grid /></el-icon>
          <span>桌位管理</span>
        </el-menu-item>
        <el-menu-item index="/orders" v-if="hasPermission('order:read')">
          <el-icon><Document /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/staff" v-if="hasPermission('staff:read')">
          <el-icon><User /></el-icon>
          <span>员工管理</span>
        </el-menu-item>
        <el-menu-item index="/roles" v-if="hasPermission('role:read')">
          <el-icon><Key /></el-icon>
          <span>角色管理</span>
        </el-menu-item>
        <el-menu-item index="/departments" v-if="hasPermission('department:read')">
          <el-icon><House /></el-icon>
          <span>部门管理</span>
        </el-menu-item>
        <el-menu-item index="/inventory" v-if="hasPermission('inventory:read')">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
        </el-menu-item>
        <el-menu-item index="/reports" v-if="hasPermission('report:dashboard')">
          <el-icon><DataAnalysis /></el-icon>
          <span>报表统计</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <span class="merchant-name">{{ merchantName }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><Avatar /></el-icon>
              {{ username }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../api/request'

const router = useRouter()
const route = useRoute()

const username = ref('')
const merchantName = ref('')
const permissions = ref([])

const activeMenu = computed(() => route.path)

// 检查是否有指定权限
const hasPermission = (permission) => {
  return permissions.value.includes(permission) || permissions.value.includes('*')
}

onMounted(async () => {
  try {
    const profile = await api.getProfile()
    username.value = profile.name || profile.username

    const merchants = await api.getMerchants()
    if (merchants.merchants?.length > 0) {
      merchantName.value = merchants.merchants[0].name
    }

    // 获取权限列表
    const perms = await api.getPermissions()
    permissions.value = perms.permissions || []
  } catch (e) {
    console.error('获取用户信息失败:', e)
  }
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    router.push('/login')
  } else if (command === 'profile') {
    // TODO: 个人信息页
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #304156;
  color: #fff;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #3d4a5c;
}

.logo h3 {
  font-size: 18px;
  margin-bottom: 4px;
}

.logo p {
  font-size: 12px;
  color: #8a97af;
}

.sidebar-menu {
  border-right: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background: #263445;
  color: #409eff;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}

.merchant-name {
  font-size: 14px;
  color: #666;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
}
</style>
