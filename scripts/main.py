#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析系统 - 主程序
支持：A 股、港股、美股
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_collector import get_quote, get_kline, get_quotes_batch
from technical_analysis import StockAnalyzer
from report_generator import ReportGenerator


def analyze_stock(code: str, market: str = 'CN', name: str = ''):
    """分析单只股票"""
    print(f"\n{'='*60}")
    print(f"📊 {name or code} ({code} - {market})")
    print('='*60)
    
    # 获取行情
    quote = get_quote(code, market)
    if not quote:
        print("❌ 获取行情失败")
        return None
    
    print(f"💰 价格：{quote.get('price', 'N/A')}")
    print(f"📈 涨跌幅：{quote.get('change_pct', 0):+.2f}%")
    
    # 获取 K 线
    kline = get_kline(code, market, count=100)
    if not kline:
        print("❌ 获取 K 线失败")
        return None
    
    print(f"📊 K 线：{len(kline)} 条")
    
    # 技术分析
    analyzer = StockAnalyzer()
    result = analyzer.analyze_stock(kline)
    
    print(f"\n📊 综合评分：{result['score']}/100")
    print(f"💡 操作建议：{result['recommendation']}")
    
    if result.get('signals'):
        print(f"\n🚨 交易信号:")
        for signal in result['signals']:
            print(f"  {signal['signal']}")
    
    return {'code': code, 'market': market, 'name': name, **quote, **result}


def main():
    """主程序"""
    parser = argparse.ArgumentParser(description='全球股票分析系统')
    parser.add_argument('--watchlist', type=str, help='自选股代码，逗号分隔')
    parser.add_argument('--market', type=str, default='CN', help='市场 (CN/HK/US)')
    parser.add_argument('--no-prompt', action='store_true', help='非交互模式')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════╗
║           🌏 全球股票分析系统 v1.0                    ║
║                                                      ║
║   支持：A 股、港股、美股                               ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 默认自选股
    default_stocks = {
        'CN': [('000001', '平安银行'), ('600519', '贵州茅台')],
        'HK': [('00700', '腾讯控股')],
        'US': [('AAPL', '苹果'), ('TSLA', '特斯拉')],
    }
    
    # 解析自选股
    if args.watchlist:
        stocks = [(c.strip(), '') for c in args.watchlist.split(',')]
    else:
        stocks = default_stocks.get(args.market.upper(), default_stocks['CN'])
    
    print(f"\n分析 {len(stocks)} 只股票 (市场：{args.market})...\n")
    
    results = []
    for code, name in stocks:
        result = analyze_stock(code, args.market, name)
        if result:
            results.append(result)
    
    # 生成报告
    if results:
        print(f"\n✅ 分析完成 {len(results)} 只股票")
        
        if not args.no_prompt:
            generator = ReportGenerator()
            generator.generate_daily_report(
                market_data={'total': len(results)},
                watchlist_analysis=results,
                save=True
            )
    else:
        print("\n❌ 无数据")


if __name__ == "__main__":
    main()
