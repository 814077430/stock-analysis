#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全球股票分析示例
演示：A 股 + 港股 + 美股 分析
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from global_collector import get_quote, get_kline
from technical_analysis import StockAnalyzer


def analyze_stock(code: str, market: str = 'CN', name: str = ''):
    """分析单只股票"""
    print(f"\n{'='*60}")
    print(f"📊 {name or code} ({code} - {market})")
    print('='*60)
    
    # 获取行情
    quote = get_quote(code, market)
    if not quote:
        print("❌ 获取行情失败")
        return
    
    print(f"💰 价格：{quote.get('price', 'N/A')}")
    print(f"📈 涨跌幅：{quote.get('change_pct', 0):+.2f}%")
    print(f"📊 成交量：{quote.get('volume', 'N/A')}")
    print(f"💵 市值：{quote.get('market_value', 'N/A')}")
    print(f"📉 市盈率：{quote.get('pe_ratio', 'N/A')}")
    
    # 获取 K 线
    kline = get_kline(code, market, 'day', 100)
    if not kline:
        print("❌ 获取 K 线失败")
        return
    
    print(f"📊 K 线数据：{len(kline)} 条")
    
    # 技术分析
    analyzer = StockAnalyzer()
    result = analyzer.analyze_stock(kline)
    
    print(f"\n📊 综合评分：{result['score']}/100")
    print(f"💡 操作建议：{result['recommendation']}")
    
    if result.get('signals'):
        print(f"\n🚨 交易信号:")
        for signal in result['signals']:
            print(f"  {signal['signal']}")


def main():
    """主程序"""
    print("""
╔══════════════════════════════════════════════════════╗
║           🌏 全球股票分析系统 v1.0                    ║
║                                                      ║
║   市场：A 股 + 港股 + 美股                              ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 检查 yfinance
    try:
        import yfinance
        print("✅ yfinance 已安装")
    except ImportError:
        print("⚠️ yfinance 未安装")
        print("   港股/美股功能不可用")
        print("   安装：pip install yfinance")
        print()
    
    # 分析股票列表
    stocks = [
        {'code': '000001', 'market': 'CN', 'name': '平安银行'},
        {'code': '600519', 'market': 'CN', 'name': '贵州茅台'},
        {'code': '00700', 'market': 'HK', 'name': '腾讯控股'},
        {'code': 'BABA', 'market': 'HK', 'name': '阿里巴巴'},
        {'code': 'AAPL', 'market': 'US', 'name': '苹果公司'},
        {'code': 'GOOGL', 'market': 'US', 'name': '谷歌'},
        {'code': 'TSLA', 'market': 'US', 'name': '特斯拉'},
        {'code': 'NVDA', 'market': 'US', 'name': '英伟达'},
    ]
    
    print(f"\n准备分析 {len(stocks)} 只股票...")
    print("="*60)
    
    for stock in stocks:
        try:
            analyze_stock(
                stock['code'],
                stock['market'],
                stock.get('name', '')
            )
        except Exception as e:
            print(f"❌ {stock['name']} 分析失败：{e}")
    
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)


if __name__ == "__main__":
    main()
