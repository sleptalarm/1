#!/bin/bash

echo "=========================================="
echo "🚀 Vercel快速部署脚本"
echo "=========================================="
echo ""

# 检查是否已经初始化git
if [ ! -d .git ]; then
    echo "📦 初始化Git仓库..."
    git init
    echo "✅ Git仓库初始化完成"
else
    echo "✅ Git仓库已存在"
fi

# 添加所有文件
echo ""
echo "📝 添加文件到Git..."
git add .

# 提交
echo ""
echo "💾 提交更改..."
git commit -m "Deploy to Vercel - $(date '+%Y-%m-%d %H:%M:%S')" || echo "没有新的更改需要提交"

# 检查是否已经添加remote
if git remote | grep -q "origin"; then
    echo ""
    echo "✅ Git remote已配置"
    echo "📤 推送到GitHub..."
    git push origin main || git push origin master
else
    echo ""
    echo "⚠️  请先在GitHub创建仓库，然后运行："
    echo ""
    echo "   git remote add origin https://github.com/YOUR-USERNAME/portfolio-tracker.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
fi

echo ""
echo "=========================================="
echo "✅ 准备完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 如果还没有，请先在GitHub创建仓库"
echo "2. 访问 https://vercel.com"
echo "3. 导入你的GitHub仓库"
echo "4. 配置MongoDB环境变量"
echo "5. 部署！"
echo ""
echo "详细步骤请查看: Vercel部署指南.md"
echo ""
