#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完美世界 (002624) 股票分析报告
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from stock_collector import StockDataCollector
from technical_analysis import StockAnalyzer
from report_generator import ReportGenerator


def analyze_wanmei():
    """分析完美世界 (002624)"""
    
    stock_code = '002624'
    stock_name = '完美世界'
    
    print("""
╔══════════════════════════════════════════════════════╗
║           📊 完美世界 (002624) 股票分析               ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 初始化
    collector = StockDataCollector()
    analyzer = StockAnalyzer()
    generator = ReportGenerator()
    
    # 1. 采集数据
    print("\n[1/4] 采集数据...")
    print(f"股票代码：{stock_code}")
    print(f"股票名称：{stock_name}")
    
    # 实时行情
    quotes = collector.eastmoney.get_realtime_quotes([stock_code])
    if quotes:
        quote = quotes[0]
        print(f"\n实时行情:")
        print(f"  现价：{quote.get('f2', 'N/A')}")
        print(f"  涨跌幅：{quote.get('f3', 'N/A')}%")
        print(f"  涨跌额：{quote.get('f4', 'N/A')}")
        print(f"  成交量：{quote.get('f5', 'N/A')}")
        print(f"  成交额：{quote.get('f6', 'N/A')}")
        print(f"  今开：{quote.get('f17', 'N/A')}")
        print(f"  最高：{quote.get('f15', 'N/A')}")
        print(f"  最低：{quote.get('f16', 'N/A')}")
        print(f"  昨收：{quote.get('f18', 'N/A')}")
    
    # 2. K 线数据
    print("\n[2/4] 获取 K 线数据...")
    kline_day = collector.eastmoney.get_kline(stock_code, 'day', 100)
    kline_week = collector.eastmoney.get_kline(stock_code, 'week', 52)
    
    if kline_day:
        print(f"  ✅ 日线数据：{len(kline_day)} 条")
        print(f"  最新日期：{kline_day[-1].get('date', 'N/A')}")
    else:
        print(f"  ❌ 获取失败")
        return
    
    # 3. 技术分析
    print("\n[3/4] 技术分析...")
    result = analyzer.analyze_stock(kline_day)
    result['code'] = stock_code
    result['name'] = stock_name
    
    print(f"\n📊 综合评分：{result['score']}/100")
    print(f"💡 操作建议：{result['recommendation']}")
    
    print(f"\n💰 价格信息:")
    price = result['price']
    print(f"  开盘：{price.get('open', 'N/A')}")
    print(f"  最高：{price.get('high', 'N/A')}")
    print(f"  最低：{price.get('low', 'N/A')}")
    print(f"  收盘：{price.get('close', 'N/A')}")
    print(f"  涨跌幅：{price.get('change_pct', 'N/A'):+.2f}%")
    
    print(f"\n📉 技术指标:")
    indicators = result['indicators']
    print(f"  MA5:  {indicators.get('MA5', 'N/A')}")
    print(f"  MA10: {indicators.get('MA10', 'N/A')}")
    print(f"  MA20: {indicators.get('MA20', 'N/A')}")
    print(f"  MA60: {indicators.get('MA60', 'N/A')}")
    print(f"  DIF:  {indicators.get('DIF', 'N/A')}")
    print(f"  DEA:  {indicators.get('DEA', 'N/A')}")
    print(f"  K:    {indicators.get('K', 'N/A')}")
    print(f"  D:    {indicators.get('D', 'N/A')}")
    print(f"  RSI6: {indicators.get('RSI6', 'N/A')}")
    
    if result['signals']:
        print(f"\n🚨 交易信号:")
        for signal in result['signals']:
            print(f"  {signal['signal']}")
    
    # 4. 生成报告
    print("\n[4/4] 生成报告...")
    report = generator.generate_stock_report(result, save=True)
    
    # 保存数据
    collector.collect_stock_detail(stock_code, save=True)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📁 报告已保存：reports/stock_{stock_code}_*.md")
    print(f"📁 数据已保存：data/stock_{stock_code}_*.json")
    
    return result


if __name__ == "__main__":
    analyze_wanmei()
