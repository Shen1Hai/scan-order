import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const API_BASE_URL = 'http://localhost:8000'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        ElMessage.error(error.response.data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default request

// API 方法
export const api = {
  // 认证
  login: (data) => request.post('/api/auth/login', data),
  getProfile: () => request.get('/api/auth/profile'),
  getPermissions: () => request.get('/api/auth/permissions'),
  getMerchants: () => request.get('/api/auth/merchants'),

  // 分类管理
  getCategories: (params) => request.get('/api/categories', { params }),
  getCategory: (id) => request.get(`/api/categories/${id}`),
  createCategory: (data) => request.post('/api/categories', data),
  updateCategory: (id, data) => request.put(`/api/categories/${id}`, data),
  deleteCategory: (id) => request.delete(`/api/categories/${id}`),

  // 菜品管理
  getDishes: (params) => request.get('/api/dishes', { params }),
  getDish: (id) => request.get(`/api/dishes/${id}`),
  createDish: (data) => request.post('/api/dishes', data),
  updateDish: (id, data) => request.put(`/api/dishes/${id}`, data),
  deleteDish: (id) => request.delete(`/api/dishes/${id}`),

  // 桌位管理
  getTables: (params) => request.get('/api/tables', { params }),
  getTable: (id) => request.get(`/api/tables/${id}`),
  getTableByCode: (code) => request.get(`/api/tables/by-code/${code}`),
  createTable: (data) => request.post('/api/tables', data),
  updateTable: (id, data) => request.put(`/api/tables/${id}`, data),
  deleteTable: (id) => request.delete(`/api/tables/${id}`),
  getTableQrcode: (id) => request.get(`/api/tables/${id}/qrcode`),
  batchGetQrcodes: () => request.post('/api/tables/batch-qrcodes'),

  // 订单管理
  getOrders: (params) => request.get('/api/orders', { params }),
  getOrder: (id) => request.get(`/api/orders/${id}`),
  getOrderByNo: (no) => request.get(`/api/orders/no/${no}`),
  updateOrderStatus: (id, data) => request.put(`/api/orders/${id}/status`, data),
  cancelOrder: (id) => request.delete(`/api/orders/${id}`),

  // 员工管理
  getStaff: (params) => request.get('/api/staff', { params }),
  getStaffMember: (id) => request.get(`/api/staff/${id}`),
  createStaff: (data) => request.post('/api/staff', data),
  updateStaff: (id, data) => request.put(`/api/staff/${id}`, data),
  deleteStaff: (id) => request.delete(`/api/staff/${id}`),

  // 库存管理
  getInventory: (params) => request.get('/api/inventory', { params }),
  getInventoryItem: (id) => request.get(`/api/inventory/${id}`),
  createInventory: (data) => request.post('/api/inventory', data),
  updateInventory: (id, data) => request.put(`/api/inventory/${id}`, data),
  deleteInventory: (id) => request.delete(`/api/inventory/${id}`),
  getInventoryLogs: (id) => request.get(`/api/inventory/${id}/logs`),
  createInventoryLog: (id, data) => request.post(`/api/inventory/${id}/log`, data),

  // 报表
  getSalesReport: (params) => request.get('/api/reports/sales', { params }),
  getDishSalesReport: (params) => request.get('/api/reports/dishes', { params }),
  getStaffReport: (params) => request.get('/api/reports/staff', { params }),
  getDashboard: () => request.get('/api/reports/dashboard'),

  // 文件上传
  uploadImage: (data) => request.post('/api/upload/image', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  // 角色管理
  getRoles: (params) => request.get('/api/roles', { params }),
  getRole: (id) => request.get(`/api/roles/${id}`),
  createRole: (data) => request.post('/api/roles', data),
  updateRole: (id, data) => request.put(`/api/roles/${id}`, data),
  deleteRole: (id) => request.delete(`/api/roles/${id}`),
  updateRolePermissions: (id, data) => request.put(`/api/roles/${id}/permissions`, data),
  getAllPermissions: () => request.get('/api/roles/permissions'),

  // 部门管理
  getDepartments: (params) => request.get('/api/departments', { params }),
  getDepartmentTree: () => request.get('/api/departments/tree'),
  getDepartment: (id) => request.get(`/api/departments/${id}`),
  createDepartment: (data) => request.post('/api/departments', data),
  updateDepartment: (id, data) => request.put(`/api/departments/${id}`, data),
  deleteDepartment: (id) => request.delete(`/api/departments/${id}`),
  setDepartmentManager: (id, managerId) => request.put(`/api/departments/${id}/manager`, null, { params: { manager_id: managerId } })
}
