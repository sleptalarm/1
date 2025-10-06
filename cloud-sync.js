/**
 * 云端数据同步模块
 * 支持与Google App Engine后端进行数据同步
 */

class CloudSync {
    constructor(apiBaseUrl = '') {
        // 如果是空字符串，使用当前域名（适用于GAE部署）
        // 如果是本地测试，可以设置为 'http://localhost:5001'
        this.apiBaseUrl = apiBaseUrl || window.location.origin;
        this.syncEnabled = true;
        this.lastSyncTime = null;
        this.syncInProgress = false;
    }

    /**
     * 检查云端同步是否可用
     */
    async checkCloudAvailability() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/health`, {
                method: 'GET',
                timeout: 5000
            });
            return response.ok;
        } catch (error) {
            console.warn('云端服务不可用:', error);
            return false;
        }
    }

    /**
     * 从云端加载投资组合数据
     */
    async loadFromCloud() {
        if (this.syncInProgress) {
            console.log('同步正在进行中，跳过本次加载');
            return null;
        }

        this.syncInProgress = true;

        try {
            console.log('正在从云端加载数据...');
            const response = await fetch(`${this.apiBaseUrl}/api/portfolio/load`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success && result.data) {
                this.lastSyncTime = new Date();
                console.log('✅ 云端数据加载成功', result.data);
                return result.data;
            } else if (result.success && result.data === null) {
                console.log('云端暂无数据');
                return null;
            } else {
                throw new Error(result.error || '加载失败');
            }
        } catch (error) {
            console.error('❌ 云端数据加载失败:', error);
            throw error;
        } finally {
            this.syncInProgress = false;
        }
    }

    /**
     * 保存投资组合数据到云端
     */
    async saveToCloud(portfolioData) {
        if (!this.syncEnabled) {
            console.log('云端同步已禁用');
            return;
        }

        if (this.syncInProgress) {
            console.log('同步正在进行中，跳过本次保存');
            return;
        }

        this.syncInProgress = true;

        try {
            console.log('正在保存到云端...', portfolioData);
            const response = await fetch(`${this.apiBaseUrl}/api/portfolio/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(portfolioData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                this.lastSyncTime = new Date();
                console.log('✅ 数据已保存到云端');
                return true;
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            console.error('❌ 云端数据保存失败:', error);
            // 不抛出错误，允许本地继续使用
            return false;
        } finally {
            this.syncInProgress = false;
        }
    }

    /**
     * 删除云端数据
     */
    async deleteFromCloud() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/portfolio/delete`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                console.log('✅ 云端数据已删除');
                return true;
            } else {
                throw new Error(result.error || '删除失败');
            }
        } catch (error) {
            console.error('❌ 云端数据删除失败:', error);
            throw error;
        }
    }

    /**
     * 获取上次同步时间
     */
    getLastSyncTime() {
        return this.lastSyncTime;
    }

    /**
     * 启用/禁用云端同步
     */
    setEnabled(enabled) {
        this.syncEnabled = enabled;
        localStorage.setItem('cloudSyncEnabled', enabled.toString());
    }

    /**
     * 检查云端同步是否启用
     */
    isEnabled() {
        const saved = localStorage.getItem('cloudSyncEnabled');
        return saved !== 'false'; // 默认启用
    }
}

// 导出为全局变量
window.CloudSync = CloudSync;
