# Vercel 一站式部署指南

使用Vercel部署整个应用，包括前端和后端API（使用Python yfinance）。

## ✅ 优势

- ✅ **完全免费**（Hobby Plan永久免费）
- ✅ **无需信用卡**
- ✅ **前端+后端一起部署**
- ✅ **自动HTTPS**
- ✅ **支持Python Serverless Functions**
- ✅ **自动从GitHub部署**
- ✅ **全球CDN加速**

## 🎯 架构说明

```
Vercel部署:
  ├── 前端 (静态文件)
  │   ├── portfolio-tracker.html
  │   ├── transactions.html
  │   └── cloud-sync.js
  │
  └── 后端API (Python Serverless)
      ├── /api/price/{symbol} - 获取股价（yfinance）
      ├── /api/history/{symbol} - 获取历史数据
      ├── /api/portfolio/save - 保存投资组合
      └── /api/portfolio/load - 加载投资组合

数据存储: MongoDB Atlas (免费512MB)
```

## 🚀 部署步骤

### 步骤1: 推送代码到GitHub

```bash
cd "/Users/shaojin/Library/CloudStorage/OneDrive-Personal/learn/tracker"

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit for Vercel deployment"

# 在GitHub创建新仓库
# 访问 https://github.com/new
# 仓库名: portfolio-tracker

# 连接到GitHub
git remote add origin https://github.com/YOUR-USERNAME/portfolio-tracker.git
git branch -M main
git push -u origin main
```

### 步骤2: 注册MongoDB Atlas（免费数据库）

1. 访问 [mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register)
2. 注册免费账号
3. 创建免费集群：
   - 选择 **M0 Free** 套餐
   - 区域选择: **AWS / N. Virginia (us-east-1)** 或离你最近的
   - 集群名称: `portfolio-tracker`
4. 创建数据库用户：
   - Username: `portfolio_user`
   - Password: 生成一个强密码（记住它）
5. 设置网络访问：
   - 点击 "Network Access"
   - 点击 "Add IP Address"
   - 选择 **"Allow Access from Anywhere"** (0.0.0.0/0)
   - 确认
6. 获取连接字符串：
   - 点击 "Connect"
   - 选择 "Connect your application"
   - 复制连接字符串，类似：
     ```
     mongodb+srv://portfolio_user:<password>@portfolio-tracker.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - 将 `<password>` 替换为你刚才设置的密码

### 步骤3: 部署到Vercel

1. **访问 [vercel.com](https://vercel.com) 并注册**
   - 用GitHub账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 选择你的GitHub仓库 `portfolio-tracker`
   - 点击 "Import"

3. **配置环境变量**
   - 在 "Configure Project" 页面
   - 展开 "Environment Variables"
   - 添加以下变量：

   ```
   名称: MONGODB_URI
   值: mongodb+srv://portfolio_user:你的密码@portfolio-tracker.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

4. **部署**
   - 点击 "Deploy"
   - 等待3-5分钟

5. **获取网址**
   - 部署成功后会得到一个网址，例如：
     ```
     https://portfolio-tracker-abc123.vercel.app
     ```

## 🎉 完成！

现在你可以：
- 在任何设备访问 `https://portfolio-tracker-abc123.vercel.app`
- 数据会自动保存到MongoDB
- 电脑和手机实时同步
- 使用yfinance获取实时股价

## 📱 测试

1. **打开网站**
   - 访问你的Vercel网址

2. **添加持仓**
   - 添加几个股票
   - 数据会自动保存到MongoDB

3. **手机测试**
   - 在手机浏览器打开相同网址
   - 应该能看到刚才添加的数据

4. **多端同步**
   - 在手机上修改数据
   - 刷新电脑浏览器
   - 应该能看到更新

## 🔧 更新代码

只需推送到GitHub，Vercel会自动重新部署：

```bash
# 修改代码后
git add .
git commit -m "Update feature"
git push

# Vercel会自动检测并重新部署
```

## 🆓 费用说明

### Vercel Free Plan
- ✅ 无限项目
- ✅ 100GB带宽/月
- ✅ 6000分钟Serverless执行时间/月
- ✅ 100次构建/月
- **个人使用完全免费**

### MongoDB Atlas Free Tier
- ✅ 512MB存储
- ✅ 共享RAM
- ✅ 永久免费
- **足够存储数千条交易记录**

## ⚙️ 配置自定义域名（可选）

1. 在Vercel项目设置中
2. 点击 "Domains"
3. 添加你的域名
4. 按照提示配置DNS

## 🐛 故障排查

### 问题1: API返回500错误

**检查：**
```bash
# 在Vercel项目中查看日志
# Dashboard → 你的项目 → Logs
```

**常见原因：**
- MongoDB连接字符串配置错误
- 密码中包含特殊字符需要URL编码

### 问题2: 无法连接MongoDB

**解决：**
1. 确认MongoDB网络访问设置为 `0.0.0.0/0`
2. 检查连接字符串中的密码是否正确
3. 密码中的特殊字符需要编码：
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`

### 问题3: yfinance获取数据慢

**说明：**
- Serverless函数首次运行会冷启动（慢）
- 后续访问会快很多
- 这是正常现象

### 问题4: 本地测试

**本地运行：**
```bash
# 安装Vercel CLI
npm install -g vercel

# 登录
vercel login

# 本地开发
vercel dev

# 访问 http://localhost:3000
```

## 📊 性能优化建议

### 1. 添加缓存
在 `vercel.json` 中添加：
```json
{
  "headers": [
    {
      "source": "/api/price/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=60, stale-while-revalidate"
        }
      ]
    }
  ]
}
```

### 2. 使用环境变量
不要在代码中硬编码API地址，使用：
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
```

## 🔒 安全建议

1. **MongoDB访问控制**
   - 生产环境建议不使用 `0.0.0.0/0`
   - 获取Vercel的出站IP并添加到白名单

2. **添加用户认证**
   - 使用Vercel Edge Config
   - 或集成第三方认证（Auth0, Firebase等）

3. **API限流**
   - 使用Vercel Edge Config
   - 防止滥用

## 📞 获取帮助

- [Vercel文档](https://vercel.com/docs)
- [MongoDB Atlas文档](https://www.mongodb.com/docs/atlas/)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

## 🎯 下一步

部署成功后，你可以：

1. **添加更多功能**
   - 价格提醒
   - 收益图表
   - 导出数据

2. **优化性能**
   - 添加缓存
   - 使用CDN

3. **增强安全性**
   - 添加用户登录
   - API认证

---

**祝部署成功！📈**


mongodb+srv://shaojinguo1_db_user:k2yrI5YgZJHXKW3h@portfolio-tracker.qec3y5l.mongodb.net/?retryWrites=true&w=majority&appName=portfolio-tracker
