"""
Vercel Serverless Function - 投资组合数据管理
使用MongoDB Atlas存储数据
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from urllib.parse import parse_qs

# 使用pymongo连接MongoDB Atlas
try:
    from pymongo import MongoClient
    from bson import ObjectId
    import hashlib
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 初始化MongoDB连接
        if MONGODB_AVAILABLE:
            mongodb_uri = os.environ.get('MONGODB_URI', '')
            if mongodb_uri:
                try:
                    # Vercel兼容的MongoDB连接配置
                    self.client = MongoClient(
                        mongodb_uri,
                        serverSelectionTimeoutMS=5000,
                        tlsAllowInvalidCertificates=True,  # 允许自签名证书
                        retryWrites=True,
                        w='majority'
                    )
                    self.db = self.client.portfolio_tracker
                    self.collection = self.db.portfolios
                except Exception as e:
                    print(f"MongoDB连接失败: {e}")
                    self.db = None
            else:
                self.db = None
        else:
            self.db = None

        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求 - 加载投资组合"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            user_id = self.get_user_id()

            if not self.db:
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Database not configured'
                }).encode())
                return

            # 从数据库加载数据
            portfolio = self.collection.find_one({'user_id': user_id})

            if portfolio:
                # 移除MongoDB的_id字段
                portfolio.pop('_id', None)
                self.wfile.write(json.dumps({
                    'success': True,
                    'data': portfolio
                }).encode())
            else:
                self.wfile.write(json.dumps({
                    'success': True,
                    'data': None
                }).encode())

        except Exception as e:
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def do_POST(self):
        """处理POST请求 - 保存投资组合"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            user_id = self.get_user_id()

            if not self.db:
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Database not configured'
                }).encode())
                return

            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            portfolio_data = json.loads(body.decode('utf-8'))

            # 添加用户ID和时间戳
            portfolio_data['user_id'] = user_id
            portfolio_data['updated_at'] = datetime.now().isoformat()

            # 更新或插入数据
            self.collection.update_one(
                {'user_id': user_id},
                {'$set': portfolio_data},
                upsert=True
            )

            self.wfile.write(json.dumps({
                'success': True,
                'message': '保存成功'
            }).encode())

        except Exception as e:
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def do_DELETE(self):
        """处理DELETE请求 - 删除投资组合"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            user_id = self.get_user_id()

            if not self.db:
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Database not configured'
                }).encode())
                return

            self.collection.delete_one({'user_id': user_id})

            self.wfile.write(json.dumps({
                'success': True,
                'message': '删除成功'
            }).encode())

        except Exception as e:
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def do_OPTIONS(self):
        """处理OPTIONS请求 - CORS预检"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def get_user_id(self):
        """获取用户ID（基于IP的哈希）"""
        # 从headers获取真实IP
        client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not client_ip:
            client_ip = self.headers.get('X-Real-IP', 'unknown')

        user_agent = self.headers.get('User-Agent', '')
        user_string = f"{client_ip}_{user_agent}"
        return hashlib.md5(user_string.encode()).hexdigest()
