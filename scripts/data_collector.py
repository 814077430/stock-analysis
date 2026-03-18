#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集模块
支持：A 股、港股、美股
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 尝试导入 yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# Windows 控制台编码处理
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# ============ 配置 ============
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


# ============ A 股数据源 ============
def get_cn_quote(stock_code: str) -> Optional[Dict]:
    """获取 A 股实时行情"""
    code = f'sh{stock_code}' if stock_code.startswith('6') else f'sz{stock_code}'
    url = f"http://qt.gtimg.cn/q={code}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'gbk'
        
        if response.text and '=' in response.text:
            parts = response.text.split('=')[1].strip('"').split('~')
            if len(parts) >= 50:
                current = float(parts[3]) if parts[3] else 0
                prev_close = float(parts[4]) if parts[4] else 0
                return {
                    'code': stock_code,
                    'name': parts[1],
                    'market': 'A 股',
                    'price': current,
                    'change_pct': ((current - prev_close) / prev_close * 100) if prev_close else 0,
                    'volume': float(parts[6]) if parts[6] else 0,
                }
        return None
    except Exception as e:
        print(f"❌ A 股 {stock_code}: {e}")
        return None


def get_cn_kline(stock_code: str, count: int = 100) -> Optional[List[Dict]]:
    """获取 A 股 K 线数据"""
    secid = f'1.{stock_code}' if stock_code.startswith('6') else f'0.{stock_code}'
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid, 'klt': 101, 'fqt': '1', 'end': '20500101',
        'lmt': count, 'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = response.json()
        
        if data.get('data') and data['data'].get('klines'):
            result = []
            for line in data['data']['klines']:
                parts = line.split(',')
                if len(parts) >= 7:
                    result.append({
                        'date': parts[0], 'open': float(parts[1]),
                        'close': float(parts[2]), 'high': float(parts[3]),
                        'low': float(parts[4]), 'volume': float(parts[5])
                    })
            return result
        return None
    except Exception as e:
        print(f"❌ A 股 K 线 {stock_code}: {e}")
        return None


# ============ 港股数据源 ============
def get_hk_quote(stock_code: str) -> Optional[Dict]:
    """获取港股实时行情"""
    if not YFINANCE_AVAILABLE:
        return None
    
    for attempt in range(3):
        try:
            time.sleep(attempt)
            code = f"{stock_code.zfill(4)}.HK" if not stock_code.endswith('.HK') else stock_code
            ticker = yf.Ticker(code)
            info = ticker.fast_info
            
            return {
                'code': stock_code, 'name': info.get('symbol', stock_code),
                'market': '港股', 'price': info.get('last_price', 0),
                'change_pct': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100 if info.get('previous_close') else 0,
                'volume': info.get('last_volume', 0),
            }
        except Exception as e:
            if attempt == 2:
                print(f"❌ 港股 {stock_code}: {e}")
                return None
            time.sleep(2)
    return None


def get_hk_kline(stock_code: str, period: str = '1mo') -> Optional[List[Dict]]:
    """获取港股 K 线数据"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        code = f"{stock_code.zfill(4)}.HK" if not stock_code.endswith('.HK') else stock_code
        ticker = yf.Ticker(code)
        history = ticker.history(period=period)
        
        result = []
        for date, row in history.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']), 'close': float(row['Close']),
                'high': float(row['High']), 'low': float(row['Low']),
                'volume': float(row['Volume'])
            })
        return result
    except Exception as e:
        print(f"❌ 港股 K 线 {stock_code}: {e}")
        return None


# ============ 美股数据源 ============
def get_us_quote(stock_code: str) -> Optional[Dict]:
    """获取美股实时行情"""
    if not YFINANCE_AVAILABLE:
        return None
    
    for attempt in range(3):
        try:
            time.sleep(attempt)
            ticker = yf.Ticker(stock_code)
            info = ticker.fast_info
            
            return {
                'code': stock_code, 'name': info.get('symbol', stock_code),
                'market': '美股', 'price': info.get('last_price', 0),
                'change_pct': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100 if info.get('previous_close') else 0,
                'volume': info.get('last_volume', 0),
            }
        except Exception as e:
            if attempt == 2:
                print(f"❌ 美股 {stock_code}: {e}")
                return None
            time.sleep(2)
    return None


def get_us_kline(stock_code: str, period: str = '1mo') -> Optional[List[Dict]]:
    """获取美股 K 线数据"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        ticker = yf.Ticker(stock_code)
        history = ticker.history(period=period)
        
        result = []
        for date, row in history.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']), 'close': float(row['Close']),
                'high': float(row['High']), 'low': float(row['Low']),
                'volume': float(row['Volume'])
            })
        return result
    except Exception as e:
        print(f"❌ 美股 K 线 {stock_code}: {e}")
        return None


# ============ 统一接口 ============
def get_quote(code: str, market: str = 'CN') -> Optional[Dict]:
    """获取实时行情"""
    market = market.upper()
    if market in ['CN', 'A', 'A 股']:
        return get_cn_quote(code)
    elif market in ['HK', 'H', '港股']:
        return get_hk_quote(code)
    elif market in ['US', 'U', '美股']:
        return get_us_quote(code)
    return None


def get_kline(code: str, market: str = 'CN', period: str = 'day', count: int = 100) -> Optional[List[Dict]]:
    """获取 K 线数据"""
    market = market.upper()
    if market in ['CN', 'A', 'A 股']:
        return get_cn_kline(code, count)
    elif market in ['HK', 'H', '港股']:
        return get_hk_kline(code, period)
    elif market in ['US', 'U', '美股']:
        return get_us_kline(code, period)
    return None


def get_quotes_batch(stocks: List[Dict], delay: int = 2) -> List[Dict]:
    """批量获取行情"""
    results = []
    for i, stock in enumerate(stocks):
        quote = get_quote(stock['code'], stock['market'])
        if quote:
            results.append(quote)
            print(f"✅ {stock['market']} {stock['code']}: {quote.get('name')} {quote.get('price')}")
        else:
            print(f"❌ {stock['market']} {stock['code']}: 获取失败")
        
        if i < len(stocks) - 1:
            time.sleep(delay)
    
    return results


# ============ 主程序 ============
def main():
    """测试示例"""
    print("🌏 全球股票数据采集 v1.0\n")
    
    test_stocks = [
        {'code': '000001', 'market': 'CN', 'name': '平安银行'},
        {'code': '600519', 'market': 'CN', 'name': '贵州茅台'},
        {'code': '00700', 'market': 'HK', 'name': '腾讯控股'},
        {'code': 'AAPL', 'market': 'US', 'name': '苹果'},
    ]
    
    print(f"测试 {len(test_stocks)} 只股票...\n")
    quotes = get_quotes_batch(test_stocks)
    print(f"\n✅ 成功 {len(quotes)}/{len(test_stocks)}")


if __name__ == "__main__":
    main()
