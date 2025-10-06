"""
Vercel Serverless Function - 投资组合数据管理
使用MongoDB Atlas Data API (HTTP REST API)
绕过SSL连接问题
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import hashlib
import urllib.request
import urllib.parse

# MongoDB Atlas Data API配置
MONGODB_DATA_API_URL = os.environ.get('MONGODB_DATA_API_URL', '')
MONGODB_API_KEY = os.environ.get('MONGODB_API_KEY', '')

class handler(BaseHTTPRequestHandler):

    def get_user_id(self):
        """获取用户ID（基于IP的哈希）"""
        client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not client_ip:
            client_ip = self.headers.get('X-Real-IP', 'unknown')
        user_agent = self.headers.get('User-Agent', '')
        user_string = f"{client_ip}_{user_agent}"
        return hashlib.md5(user_string.encode()).hexdigest()

    def mongodb_request(self, action, filter_doc=None, document=None, update=None):
        """
        使用MongoDB Data API发送请求

        action: 'findOne', 'insertOne', 'updateOne', 'deleteOne'
        """
        if not MONGODB_DATA_API_URL or not MONGODB_API_KEY:
            return {'error': 'MongoDB Data API not configured'}

        payload = {
            "dataSource": "Cluster0",  # 你的集群名称
            "database": "portfolio_tracker",
            "collection": "portfolios"
        }

        if filter_doc:
            payload["filter"] = filter_doc
        if document:
            payload["document"] = document
        if update:
            payload["update"] = update

        # 构建URL
        url = f"{MONGODB_DATA_API_URL}/action/{action}"

        # 构建请求
        headers = {
            'Content-Type': 'application/json',
            'api-key': MONGODB_API_KEY
        }

        data = json.dumps(payload).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {'error': str(e)}

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

            # 使用Data API查询
            result = self.mongodb_request('findOne', filter_doc={'user_id': user_id})

            if 'error' in result:
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': result['error']
                }).encode())
                return

            if result.get('document'):
                # 移除MongoDB的_id字段
                doc = result['document']
                doc.pop('_id', None)
                self.wfile.write(json.dumps({
                    'success': True,
                    'data': doc
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

            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            portfolio_data = json.loads(body.decode('utf-8'))

            # 添加用户ID和时间戳
            portfolio_data['user_id'] = user_id
            portfolio_data['updated_at'] = datetime.now().isoformat()

            # 使用Data API更新或插入
            result = self.mongodb_request(
                'updateOne',
                filter_doc={'user_id': user_id},
                update={'$set': portfolio_data}
            )

            # 如果没有匹配的文档，插入新文档
            if result.get('matchedCount', 0) == 0:
                result = self.mongodb_request(
                    'insertOne',
                    document=portfolio_data
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

            result = self.mongodb_request('deleteOne', filter_doc={'user_id': user_id})

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
