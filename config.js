/**
 * API配置文件
 * 根据环境自动切换API地址
 */

const CONFIG = {
    // API基础URL - 自动使用当前域名
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:5001'  // 本地开发
        : window.location.origin,  // 生产环境使用当前域名

    // 是否启用云端同步
    ENABLE_CLOUD_SYNC: true,

    // 数据库类型：'firestore', 'mongodb', 'localstorage'
    DATABASE_TYPE: 'mongodb',  // 使用MongoDB云端存储
};

// 导出配置
window.APP_CONFIG = CONFIG;
