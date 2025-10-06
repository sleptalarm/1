"""
Vercel调试接口 - 检查环境变量和配置
访问: /api/debug
"""

from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # 检查环境变量（不显示完整密码）
        mongodb_uri = os.environ.get('MONGODB_URI', 'NOT_SET')

        # 隐藏敏感信息
        if mongodb_uri != 'NOT_SET' and len(mongodb_uri) > 30:
            mongodb_status = f"{mongodb_uri[:30]}...{mongodb_uri[-10:]}"
        else:
            mongodb_status = mongodb_uri

        debug_info = {
            'status': 'ok',
            'environment': {
                'MONGODB_URI_SET': mongodb_uri != 'NOT_SET',
                'MONGODB_URI_PREVIEW': mongodb_status,
                'MONGODB_URI_LENGTH': len(mongodb_uri) if mongodb_uri != 'NOT_SET' else 0
            },
            'vercel': {
                'region': os.environ.get('VERCEL_REGION', 'unknown'),
                'env': os.environ.get('VERCEL_ENV', 'unknown')
            },
            'available_imports': {
                'pymongo': False,
                'yfinance': False,
                'pandas': False
            }
        }

        # 检查依赖是否可用
        try:
            import pymongo
            debug_info['available_imports']['pymongo'] = True
            debug_info['pymongo_version'] = pymongo.__version__
        except ImportError:
            pass

        try:
            import yfinance
            debug_info['available_imports']['yfinance'] = True
        except ImportError:
            pass

        try:
            import pandas
            debug_info['available_imports']['pandas'] = True
        except ImportError:
            pass

        # 测试MongoDB连接（如果配置了）
        if mongodb_uri != 'NOT_SET':
            try:
                from pymongo import MongoClient
                client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                # 尝试连接
                client.admin.command('ping')
                debug_info['mongodb_connection'] = 'SUCCESS'
                client.close()
            except Exception as e:
                debug_info['mongodb_connection'] = f'FAILED: {str(e)}'
        else:
            debug_info['mongodb_connection'] = 'NOT_CONFIGURED'

        self.wfile.write(json.dumps(debug_info, indent=2).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
