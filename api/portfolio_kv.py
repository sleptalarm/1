"""
Vercel Serverless Function - 投资组合数据管理
使用Redis存储数据
完美兼容Vercel，无SSL问题
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import hashlib

# 尝试导入redis库
try:
    import redis
    REDIS_URL = os.environ.get('REDIS_URL', '')
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        REDIS_AVAILABLE = True
    else:
        REDIS_AVAILABLE = False
except Exception as e:
    REDIS_AVAILABLE = False
    redis_client = None

def kv_get(key):
    """从Redis获取数据"""
    if not REDIS_AVAILABLE:
        return None

    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis GET error: {e}")
        return None

def kv_set(key, value):
    """保存数据到Redis"""
    if not REDIS_AVAILABLE:
        raise Exception("Redis未配置")

    try:
        redis_client.set(key, json.dumps(value))
        return True
    except Exception as e:
        raise Exception(f"Redis SET error: {e}")

def kv_delete(key):
    """从Redis删除数据"""
    if not REDIS_AVAILABLE:
        raise Exception("Redis未配置")

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        raise Exception(f"Redis DELETE error: {e}")

class handler(BaseHTTPRequestHandler):

    def get_user_id(self):
        """获取用户ID（使用固定ID以支持多设备同步）"""
        # 使用固定用户ID，所有设备共享同一份数据
        # 如需多用户支持，可以添加登录系统
        return "default_user"

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
