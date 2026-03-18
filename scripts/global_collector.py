#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全球股票数据采集模块
支持：A 股、港股、美股
"""

import sys
import json
import requests

# Windows 控制台编码处理
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 尝试导入 yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance 未安装，港股/美股功能不可用")
    print("   安装：pip install yfinance")

# ============ 配置 ============
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


# ============ A 股数据源 (腾讯 API) ============
def get_cn_quote(stock_code: str) -> Optional[Dict]:
    """获取 A 股实时行情"""
    if stock_code.startswith('6'):
        code = f'sh{stock_code}'
    else:
        code = f'sz{stock_code}'
    
    url = f"http://qt.gtimg.cn/q={code}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'gbk'
        
        if response.text and '=' in response.text:
            data_part = response.text.split('=')[1].strip('"')
            parts = data_part.split('~')
            
            if len(parts) >= 50:
                current = float(parts[3]) if parts[3] else 0
                prev_close = float(parts[4]) if parts[4] else 0
                
                return {
                    'code': stock_code,
                    'name': parts[1],
                    'market': 'A 股',
                    'price': current,
                    'open': float(parts[5]) if parts[5] else 0,
                    'high': float(parts[33]) if parts[33] else 0,
                    'low': float(parts[34]) if parts[34] else 0,
                    'close': prev_close,
                    'change': current - prev_close,
                    'change_pct': ((current - prev_close) / prev_close * 100) if prev_close else 0,
                    'volume': float(parts[6]) if parts[6] else 0,
                    'amount': float(parts[37]) * 100 if len(parts) > 37 and parts[37] else 0,
                    'market_value': float(parts[45]) if len(parts) > 45 and parts[45] else 0,
                    'pe_ratio': float(parts[39]) if len(parts) > 39 and parts[39] else 0
                }
        return None
    except Exception as e:
        print(f"❌ 获取 A 股行情失败 {stock_code}: {e}")
        return None


# ============ 港股/美股数据源 (yfinance) ============
def get_hk_quote(stock_code: str) -> Optional[Dict]:
    """获取港股实时行情"""
    if not YFINANCE_AVAILABLE:
        return None
    
    import time
    # 重试机制
    for attempt in range(3):
        try:
            time.sleep(1 * attempt)  # 重试前等待
            
            # 港股代码格式：0700.HK
            if not stock_code.endswith('.HK'):
                code = f"{stock_code.zfill(4)}.HK"
            else:
                code = stock_code
            
            ticker = yf.Ticker(code)
            info = ticker.fast_info
            
            return {
                'code': stock_code,
                'name': info.get('symbol', stock_code),
                'market': '港股',
                'price': info.get('last_price', 0),
                'open': info.get('open', 0),
                'high': info.get('day_high', 0),
                'low': info.get('day_low', 0),
                'close': info.get('previous_close', 0),
                'change': info.get('last_price', 0) - info.get('previous_close', 0),
                'change_pct': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100 if info.get('previous_close') else 0,
                'volume': info.get('last_volume', 0),
                'market_value': info.get('market_cap', 0),
                'pe_ratio': info.get('trailing_pe', 0)
            }
        except Exception as e:
            if attempt == 2:
                print(f"❌ 获取港股行情失败 {stock_code}: {e}")
                return None
            time.sleep(2)
    
    return None


def get_us_quote(stock_code: str) -> Optional[Dict]:
    """获取美股实时行情"""
    if not YFINANCE_AVAILABLE:
        return None
    
    import time
    # 重试机制
    for attempt in range(3):
        try:
            time.sleep(1 * attempt)  # 重试前等待
            
            # 美股代码格式：AAPL
            ticker = yf.Ticker(stock_code)
            info = ticker.fast_info
            
            return {
                'code': stock_code,
                'name': info.get('symbol', stock_code),
                'market': '美股',
                'price': info.get('last_price', 0),
                'open': info.get('open', 0),
                'high': info.get('day_high', 0),
                'low': info.get('day_low', 0),
                'close': info.get('previous_close', 0),
                'change': info.get('last_price', 0) - info.get('previous_close', 0),
                'change_pct': ((info.get('last_price', 0) - info.get('previous_close', 0)) / info.get('previous_close', 1)) * 100 if info.get('previous_close') else 0,
                'volume': info.get('last_volume', 0),
                'market_value': info.get('market_cap', 0),
                'pe_ratio': info.get('trailing_pe', 0)
            }
        except Exception as e:
            if attempt == 2:
                print(f"❌ 获取美股行情失败 {stock_code}: {e}")
                return None
            time.sleep(2)
    
    return None


# ============ K 线数据 ============
def get_kline_cn(stock_code: str, period: str = 'day', count: int = 100) -> Optional[List[Dict]]:
    """获取 A 股 K 线数据"""
    if stock_code.startswith('6'):
        secid = f'1.{stock_code}'
    else:
        secid = f'0.{stock_code}'
    
    period_map = {'day': 101, 'week': 102, 'month': 103}
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid,
        'klt': period_map.get(period, 101),
        'fqt': '1',
        'end': '20500101',
        'lmt': count,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            result = []
            for line in klines:
                parts = line.split(',')
                if len(parts) >= 11:
                    result.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]),
                        'amplitude': float(parts[7]),
                        'chg': float(parts[8]),
                        'change': float(parts[9]),
                        'turnover': float(parts[10])
                    })
            return result
        return None
    except Exception as e:
        print(f"❌ 获取 A 股 K 线失败 {stock_code}: {e}")
        return None


def get_kline_global(stock_code: str, market: str = 'US', period: str = '1mo') -> Optional[List[Dict]]:
    """获取港股/美股 K 线数据"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        # 代码格式转换
        if market == 'HK':
            code = f"{stock_code}.HK"
        elif market == 'US':
            code = stock_code
        else:
            code = stock_code
        
        ticker = yf.Ticker(code)
        history = ticker.history(period=period)
        
        result = []
        for date, row in history.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'close': float(row['Close']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': float(row['Volume']),
                'amount': 0,
                'amplitude': 0,
                'chg': 0,
                'change': 0,
                'turnover': 0
            })
        
        return result
    except Exception as e:
        print(f"❌ 获取全球 K 线失败 {stock_code}: {e}")
        return None


# ============ 统一接口 ============
def get_quote(stock_code: str, market: str = 'CN') -> Optional[Dict]:
    """
    获取实时行情 (统一接口)
    
    Args:
        stock_code: 股票代码
        market: 市场 (CN/A 股，HK/港股，US/美股)
    
    Returns:
        行情数据字典
    """
    market = market.upper()
    
    if market in ['CN', 'A', 'A 股']:
        return get_cn_quote(stock_code)
    elif market in ['HK', 'H', '港股']:
        return get_hk_quote(stock_code)
    elif market in ['US', 'U', '美股', 'USA']:
        return get_us_quote(stock_code)
    else:
        print(f"⚠️ 未知市场类型：{market}")
        return None


def get_kline(stock_code: str, market: str = 'CN', period: str = 'day', count: int = 100) -> Optional[List[Dict]]:
    """
    获取 K 线数据 (统一接口)
    
    Args:
        stock_code: 股票代码
        market: 市场 (CN/HK/US)
        period: 周期 (day/week/month 或 1d/5d/1mo 等)
        count: 数量
    
    Returns:
        K 线数据列表
    """
    market = market.upper()
    
    if market in ['CN', 'A', 'A 股']:
        return get_kline_cn(stock_code, period, count)
    elif market in ['HK', 'H', '港股']:
        return get_kline_global(stock_code, 'HK', period)
    elif market in ['US', 'U', '美股', 'USA']:
        return get_kline_global(stock_code, 'US', period)
    else:
        print(f"⚠️ 未知市场类型：{market}")
        return None


# ============ 批量获取 ============
def get_quotes_batch(stocks: List[Dict]) -> List[Dict]:
    """
    批量获取行情
    
    Args:
        stocks: 股票列表 [{'code': '000001', 'market': 'CN'}, ...]
    
    Returns:
        行情数据列表
    """
    results = []
    
    for stock in stocks:
        code = stock.get('code')
        market = stock.get('market', 'CN')
        
        quote = get_quote(code, market)
        if quote:
            results.append(quote)
            print(f"✅ {market} {code}: {quote.get('name', 'N/A')} {quote.get('price', 'N/A')}")
        else:
            print(f"❌ {market} {code}: 获取失败")
    
    return results


# ============ 主程序 ============
def main():
    """测试示例"""
    print("""
╔══════════════════════════════════════════════════════╗
║           🌏 全球股票数据采集 v1.0                    ║
║                                                      ║
║   支持：A 股、港股、美股                               ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 测试股票列表
    test_stocks = [
        {'code': '000001', 'market': 'CN'},   # 平安银行
        {'code': '600519', 'market': 'CN'},   # 贵州茅台
        {'code': '00700', 'market': 'HK'},    # 腾讯控股
        {'code': 'AAPL', 'market': 'US'},     # 苹果
        {'code': 'TSLA', 'market': 'US'},     # 特斯拉
    ]
    
    print("\n批量获取行情...")
    quotes = get_quotes_batch(test_stocks)
    
    print(f"\n✅ 成功获取 {len(quotes)} 只股票行情")
    
    # 保存数据
    if quotes:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = DATA_DIR / f'global_quotes_{timestamp}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quotes, f, ensure_ascii=False, indent=2)
        print(f"📁 数据已保存：{filepath}")


if __name__ == "__main__":
    main()
