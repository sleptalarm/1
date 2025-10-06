"""
Vercel Serverless Function - 投资组合数据管理
使用Vercel KV (Redis) 存储数据，通过REST API访问
完美兼容Vercel，无SSL问题，无需额外依赖
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import hashlib
import urllib.request
import urllib.error

# Vercel自动注入的KV环境变量
KV_REST_API_URL = os.environ.get('KV_REST_API_URL', '')
KV_REST_API_TOKEN = os.environ.get('KV_REST_API_TOKEN', '')

def kv_get(key):
    """从Vercel KV获取数据"""
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        return None

    url = f"{KV_REST_API_URL}/get/{key}"
    headers = {'Authorization': f'Bearer {KV_REST_API_TOKEN}'}

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            if result == 'null' or not result:
                return None
            data = json.loads(result)
            return data.get('result')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def kv_set(key, value):
    """保存数据到Vercel KV"""
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        raise Exception("KV环境变量未配置")

    url = f"{KV_REST_API_URL}/set/{key}"
    data = json.dumps(value).encode('utf-8')
    headers = {
        'Authorization': f'Bearer {KV_REST_API_TOKEN}',
        'Content-Type': 'application/json'
    }

    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def kv_delete(key):
    """从Vercel KV删除数据"""
    if not KV_REST_API_URL or not KV_REST_API_TOKEN:
        raise Exception("KV环境变量未配置")

    url = f"{KV_REST_API_URL}/del/{key}"
    headers = {'Authorization': f'Bearer {KV_REST_API_TOKEN}'}

    req = urllib.request.Request(url, headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

class handler(BaseHTTPRequestHandler):

    def get_user_id(self):
        """获取用户ID（基于IP的哈希）"""
        client_ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not client_ip:
            client_ip = self.headers.get('X-Real-IP', 'unknown')
        user_agent = self.headers.get('User-Agent', '')
        user_string = f"{client_ip}_{user_agent}"
        return hashlib.md5(user_string.encode()).hexdigest()

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
            key = f"portfolio:{user_id}"

            # 从KV获取数据
            data = kv_get(key)

            if data:
                # KV返回的可能是字符串，需要解析
                if isinstance(data, str):
                    data = json.loads(data)

                self.wfile.write(json.dumps({
                    'success': True,
                    'data': data
                }).encode())
            else:
                # 返回默认空数据
                self.wfile.write(json.dumps({
                    'success': True,
                    'data': {
                        'portfolio': {},
                        'cashBalance': 100000,
                        'transactionHistory': []
                    }
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
            key = f"portfolio:{user_id}"

            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            portfolio_data = json.loads(body.decode('utf-8'))

            # 添加时间戳
            portfolio_data['updated_at'] = datetime.now().isoformat()

            # 保存到KV
            kv_set(key, portfolio_data)

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
            key = f"portfolio:{user_id}"

            kv_delete(key)

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
