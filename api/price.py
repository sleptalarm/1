"""
Vercel Serverless Function - 获取股票价格
使用 yfinance 获取Yahoo Finance数据
"""

from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析URL
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')

        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            # 路由: /api/price/{symbol}
            if len(path_parts) >= 3 and path_parts[1] == 'price':
                symbol = path_parts[2].upper()
                result = self.get_current_price(symbol)
                self.wfile.write(json.dumps(result).encode())

            # 路由: /api/history/{symbol}
            elif len(path_parts) >= 3 and path_parts[1] == 'history':
                symbol = path_parts[2].upper()
                # 解析查询参数
                query_params = parse_qs(parsed_path.query)
                period = query_params.get('period', ['1M'])[0]
                result = self.get_historical_data(symbol, period)
                self.wfile.write(json.dumps(result).encode())

            # 路由: /api/health
            elif len(path_parts) >= 2 and path_parts[1] == 'health':
                result = {
                    'status': 'ok',
                    'message': '股票追踪API服务正常运行',
                    'timestamp': datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(result).encode())

            else:
                self.wfile.write(json.dumps({
                    'error': 'Invalid endpoint',
                    'usage': {
                        'price': '/api/price/{symbol}',
                        'history': '/api/history/{symbol}?period=1M',
                        'health': '/api/health'
                    }
                }).encode())

        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def get_current_price(self, symbol):
        """获取当前股价"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_price is None:
                # 尝试从历史数据获取最新价格
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])

            if current_price is None:
                return {'error': f'无法获取 {symbol} 的股价数据'}

            return {
                'success': True,
                'symbol': symbol,
                'price': float(current_price),
                'company_name': info.get('longName', symbol),
                'currency': info.get('currency', 'USD'),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取股价失败: {str(e)}'
            }

    def get_historical_data(self, symbol, period):
        """获取历史股价数据"""
        try:
            # 根据时间范围设置获取的天数
            period_days = {
                '1D': 20,
                '1W': 65,
                '1M': 250,
                '3M': 750,
                '6M': 1500,
                'YTD': 365
            }

            days = period_days.get(period, 250)

            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                return {
                    'success': False,
                    'error': f'无法获取 {symbol} 的历史数据'
                }

            # 转换数据格式
            data = []
            for date_index, row in hist.iterrows():
                data.append({
                    'date': date_index.date().strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })

            return {
                'success': True,
                'symbol': symbol,
                'period': period,
                'data': data,
                'count': len(data)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'获取历史数据失败: {str(e)}'
            }
