# 股票投资组合追踪器 - Vercel云端版

一个支持多端同步的股票投资组合追踪工具，使用Python yfinance获取实时股价，完全免费部署到Vercel。

## ✨ 特性

- 📈 **实时股价**: 使用yfinance从Yahoo Finance获取实时数据
- ☁️ **云端同步**: MongoDB Atlas免费数据库，多端实时同步
- 📱 **多设备支持**: 电脑、手机、平板无缝切换
- 🚀 **一键部署**: Vercel一站式托管前后端
- 💰 **完全免费**: Vercel + MongoDB Atlas免费套餐
- 📊 **完整功能**: 持仓管理、交易记录、收益分析、图表展示

## 🎯 技术栈

### 前端
- HTML/CSS/JavaScript
- Chart.js (图表)
- LocalStorage (本地缓存)

### 后端
- Python 3.9 (Vercel Serverless Functions)
- yfinance (股票数据)
- pandas (数据处理)
- pymongo (MongoDB连接)

### 数据库
- MongoDB Atlas (免费512MB)

## 📂 项目结构

```
tracker/
├── api/                          # Vercel Serverless Functions
│   ├── price.py                  # 股价API (yfinance)
│   ├── portfolio.py              # 投资组合数据API
│   └── requirements.txt          # Python依赖
├── portfolio-tracker.html        # 主页面
├── transactions.html             # 交易记录页面
├── cloud-sync.js                 # 云端同步模块
├── config.js                     # 配置文件
├── vercel.json                   # Vercel配置
├── .vercelignore                 # 部署忽略文件
└── Vercel部署指南.md             # 📖 详细部署文档
```

## 🚀 快速部署（5分钟）

### 步骤1: 推送到GitHub

```bash
cd "/Users/shaojin/Library/CloudStorage/OneDrive-Personal/learn/tracker"

git init
git add .
git commit -m "Deploy to Vercel"
git remote add origin https://github.com/YOUR-USERNAME/portfolio-tracker.git
git push -u origin main
```

### 步骤2: 注册免费数据库

1. 访问 [mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. 创建免费M0集群
3. 获取连接字符串（记住密码）

### 步骤3: 部署到Vercel

1. 访问 [vercel.com](https://vercel.com) 并用GitHub登录
2. 导入你的GitHub仓库
3. 添加环境变量：
   ```
   MONGODB_URI = mongodb+srv://user:password@...
   ```
4. 点击部署

### 步骤4: 完成！

访问你的网址，例如：`https://portfolio-tracker-abc123.vercel.app`

**详细步骤请查看** → [Vercel部署指南.md](Vercel部署指南.md)

## 💻 本地测试

```bash
# 安装依赖
pip install flask flask-cors yfinance pandas

# 运行本地服务器
python app.py

# 访问 http://localhost:5001
```

## 📱 使用方法

1. **访问网站** - 打开你的Vercel网址
2. **添加持仓** - 输入股票代码（如AAPL、TSLA）
3. **实时价格** - 自动获取最新股价
4. **交易记录** - 记录所有买卖操作
5. **多端同步** - 手机电脑数据自动同步

## 🆓 完全免费

- **Vercel**: 100GB带宽/月，永久免费
- **MongoDB Atlas**: 512MB存储，永久免费
- **Yahoo Finance**: 免费股票数据
- **总费用**: $0/月 🎉

## 📖 文档

- **[Vercel部署指南.md](Vercel部署指南.md)** ⭐ 详细部署教程
- 包含故障排查、性能优化、安全建议

## 🛠️ 本地开发（可选）

```bash
# 安装Vercel CLI
npm install -g vercel

# 本地运行（完整模拟生产环境）
vercel dev

# 访问 http://localhost:3000
```

## 🔒 安全说明

当前版本使用IP地址识别用户，适合个人使用。

如需更高安全性：
- 添加用户认证系统
- 配置MongoDB网络白名单
- 使用环境变量保护API密钥

## 📊 支持的股票市场

- 🇺🇸 美股: AAPL, MSFT, GOOGL, TSLA
- 🇭🇰 港股: 0700.HK, 9988.HK
- 🇨🇳 A股: 000001.SS, 600519.SS

## 🐛 故障排查

详见 [Vercel部署指南.md](Vercel部署指南.md#故障排查) 的完整说明。

常见问题：
- API返回500 → 检查MongoDB连接字符串
- 数据不同步 → 确认环境变量已配置
- 价格获取慢 → Serverless冷启动正常现象

## 📞 获取帮助

1. 查看 [Vercel部署指南.md](Vercel部署指南.md)
2. 检查Vercel项目日志
3. 检查浏览器控制台错误

## 📄 许可证

MIT License - 自由使用和修改

---

**🚀 开始部署**: 查看 [Vercel部署指南.md](Vercel部署指南.md)
**💬 需要帮助**: 提交Issue或查看文档
