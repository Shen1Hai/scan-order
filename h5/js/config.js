/**
 * H5 顾客端 - API 配置
 */

const CONFIG = {
    // API 基础地址（根据实际部署修改）
    API_BASE_URL: 'http://localhost:8000',

    // WebSocket 地址
    WS_URL: 'ws://localhost:8000/ws',

    // 应用名称
    APP_NAME: '扫码点单',

    // 桌位编码（从 URL 参数获取）
    TABLE_CODE: null,

    // 桌位 ID（扫码后获取）
    TABLE_ID: null,

    // 表单数据用于提交订单
    TABLE_NAME: null
};

// 从 URL 解析桌位编码
function parseTableCode() {
    const params = new URLSearchParams(window.location.search);
    CONFIG.TABLE_CODE = params.get('table') || params.get('tableCode');

    // 也支持 path 格式: /h5/?table=T01
    const pathMatch = window.location.pathname.match(/\/table\/([^\/]+)/);
    if (pathMatch) {
        CONFIG.TABLE_CODE = pathMatch[1];
    }
}

// 获取完整 API URL
function getApiUrl(path) {
    return CONFIG.API_BASE_URL + path;
}
