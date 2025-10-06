#!/usr/bin/env python3
"""
股票投资组合追踪器 - 云端版本 (Google App Engine)
支持多端同步
"""

import os
import sys
import threading
import webbrowser
import time
import socket
import requests
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import hashlib

# 云端数据库导入（仅在GAE环境时使用）
try:
    from firestore_db import PortfolioDatabase
    USE_FIRESTORE = True
except ImportError:
    USE_FIRESTORE = False
    print("⚠️ Firestore未启用，数据将不会持久化")

# 获取应用程序路径，支持PyInstaller打包
def get_resource_path(relative_path):
    """获取资源文件路径，适配PyInstaller"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Flask应用设置
app = Flask(__name__,
            static_folder=get_resource_path('.'),
            static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# 初始化数据库
if USE_FIRESTORE:
    db = PortfolioDatabase()
else:
    db = None

def get_user_id():
    """获取用户ID（基于IP地址生成唯一ID）"""
    # 在生产环境中，建议使用更完善的用户认证系统
    # 这里使用IP地址的哈希作为临时方案
    client_ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', '')
    user_string = f"{client_ip}_{user_agent}"
    return hashlib.md5(user_string.encode()).hexdigest()

@app.route('/')
def index():
    """主页面"""
    return app.send_static_file('portfolio-tracker.html')

@app.route('/transactions.html')
def transactions():
    """交易记录页面"""
    return app.send_static_file('transactions.html')

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '股票追踪API服务正常运行',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/price/<symbol>')
def get_current_price(symbol):
    """获取当前股价"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if current_price is None:
            # 尝试从历史数据获取最新价格
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])

        if current_price is None:
            return jsonify({'error': f'无法获取 {symbol} 的股价数据'}), 404

        response = {
            'success': True,
            'symbol': symbol.upper(),
            'price': float(current_price),
            'company_name': info.get('longName', symbol.upper()),
            'currency': info.get('currency', 'USD'),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取股价失败: {str(e)}'
        }), 500

@app.route('/api/history/<symbol>')
def get_historical_data(symbol):
    """获取历史股价数据"""
    try:
        period = request.args.get('period', '1M')

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

        ticker = yf.Ticker(symbol.upper())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        hist = ticker.history(start=start_date, end=end_date)

        if hist.empty:
            return jsonify({
                'success': False,
                'error': f'无法获取 {symbol} 的历史数据'
            }), 404

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

        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'period': period,
            'data': data,
            'count': len(data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取历史数据失败: {str(e)}'
        }), 500

# ==================== 云端数据同步API ====================

@app.route('/api/portfolio/save', methods=['POST'])
def save_portfolio():
    """保存投资组合数据到云端"""
    if not USE_FIRESTORE:
        return jsonify({
            'success': False,
            'error': 'Firestore未启用，无法保存数据'
        }), 503

    try:
        user_id = get_user_id()
        portfolio_data = request.get_json()

        if not portfolio_data:
            return jsonify({
                'success': False,
                'error': '无效的数据'
            }), 400

        result = db.save_portfolio(user_id, portfolio_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }), 500

@app.route('/api/portfolio/load', methods=['GET'])
def load_portfolio():
    """从云端加载投资组合数据"""
    if not USE_FIRESTORE:
        return jsonify({
            'success': False,
            'error': 'Firestore未启用，无法加载数据'
        }), 503

    try:
        user_id = get_user_id()
        result = db.get_portfolio(user_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'加载失败: {str(e)}'
        }), 500

@app.route('/api/portfolio/delete', methods=['DELETE'])
def delete_portfolio():
    """删除云端投资组合数据"""
    if not USE_FIRESTORE:
        return jsonify({
            'success': False,
            'error': 'Firestore未启用，无法删除数据'
        }), 503

    try:
        user_id = get_user_id()
        result = db.delete_portfolio(user_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500

def is_port_in_use(port, host='localhost'):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def wait_for_server_and_open_browser():
    """等待服务器启动完成后自动打开浏览器"""
    max_attempts = 30
    server_url = "http://localhost:5001"

    print("🌐 等待服务器启动完成...")

    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{server_url}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ 服务器已就绪，正在打开浏览器...")
                time.sleep(1)
                webbrowser.open(server_url)
                print(f"🎉 已自动打开网页: {server_url}")
                return
        except (requests.RequestException, requests.ConnectionError):
            time.sleep(1)
            if attempt % 5 == 0:  # 每5秒打印一次状态
                print(f"   正在等待服务器启动... ({attempt + 1}/{max_attempts})")

    print("⚠️ 服务器启动超时，请手动访问: http://localhost:5001")

def main():
    print("=" * 60)
    print("🚀 股票投资组合追踪器")
    print("=" * 60)

    server_port = 5001
    server_url = f"http://localhost:{server_port}"

    # 检查端口是否已被占用
    print(f"🔍 检查端口 {server_port}...")
    if is_port_in_use(server_port):
        print(f"✅ 端口 {server_port} 已被占用，服务器可能已在运行")
        print("🌐 直接打开网页...")
        try:
            webbrowser.open(server_url)
            print(f"🎉 已打开网页: {server_url}")
            print("💡 如需停止服务器，请按 Ctrl+C")
        except Exception as e:
            print(f"⚠️ 打开浏览器失败: {e}")
            print(f"请手动访问: {server_url}")
        return

    print(f"📍 端口 {server_port} 空闲，启动服务器...")
    print()

    # 在后台线程中等待服务器启动并打开浏览器
    browser_thread = threading.Thread(target=wait_for_server_and_open_browser, daemon=True)
    browser_thread.start()

    try:
        print("🌐 启动Flask服务器...")
        print(f"📍 服务地址: {server_url}")
        print("🛑 按 Ctrl+C 停止服务")
        print("-" * 60)

        # 启动Flask应用
        app.run(host='0.0.0.0', port=server_port, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == '__main__':
    main()