#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析系统 - 主程序
整合数据采集、技术分析、报告生成
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from stock_collector import StockDataCollector
from technical_analysis import StockAnalyzer
from report_generator import ReportGenerator


def run_full_analysis(watchlist: list = None):
    """
    完整分析流程：采集 → 分析 → 报告
    """
    print("""
╔══════════════════════════════════════════════════════╗
║           📈 股票分析系统 v1.0                        ║
║                                                      ║
║   数据采集 → 技术分析 → 报告生成                      ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 默认自选股
    if watchlist is None:
        watchlist = ['000001', '600000', '000002', '600519', '000858']
    
    collector = StockDataCollector()
    analyzer = StockAnalyzer()
    generator = ReportGenerator()
    
    # 1. 采集数据
    print("\n" + "=" * 60)
    print("📥 [1/4] 采集数据...")
    print("=" * 60)
    
    # 采集全市场快照
    market_data = collector.collect_all_stocks(save=True)
    print(f"✅ 全市场股票：{market_data['total_stocks']} 只")
    
    # 采集自选股
    print(f"\n采集自选股 ({len(watchlist)} 只)...")
    watchlist_data = collector.collect_watchlist(watchlist, save=True)
    
    # 2. 采集 K 线并分析
    print("\n" + "=" * 60)
    print("📊 [2/4] 技术分析...")
    print("=" * 60)
    
    watchlist_analysis = []
    for code in watchlist:
        print(f"\n分析 {code}...")
        
        # 获取 K 线
        kline_data = collector.eastmoney.get_kline(code, 'day', 100)
        
        if kline_data:
            # 技术分析
            result = analyzer.analyze_stock(kline_data)
            result['code'] = code
            
            # 获取股票名称
            if watchlist_data:
                for q in watchlist_data:
                    if q.get('f12') == code:
                        result['name'] = q.get('f14', 'Unknown')
                        break
            
            watchlist_analysis.append(result)
            
            # 简要显示
            print(f"  💰 价格：{result['price']['close']} ({result['price']['change_pct']:+.2f}%)")
            print(f"  📊 评分：{result['score']}/100")
            print(f"  💡 建议：{result['recommendation']}")
        else:
            print(f"  ⚠️ 无数据")
    
    # 3. 生成报告
    print("\n" + "=" * 60)
    print("📄 [3/4] 生成报告...")
    print("=" * 60)
    
    # 日报
    print("\n生成日报...")
    generator.generate_daily_report(
        market_data=market_data,
        watchlist_analysis=watchlist_analysis,
        save=True
    )
    
    # 个股报告
    print("生成个股报告...")
    for stock in watchlist_analysis[:3]:  # 前 3 只
        generator.generate_stock_report(stock, save=True)
    
    # 4. 保存汇总
    print("\n" + "=" * 60)
    print("💾 [4/4] 保存汇总...")
    print("=" * 60)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'market_overview': {
            'total_stocks': market_data['total_stocks'],
            'sh_count': market_data['sh_count'],
            'sz_count': market_data['sz_count'],
            'bj_count': market_data['bj_count']
        },
        'watchlist_summary': [
            {
                'code': s.get('code'),
                'name': s.get('name'),
                'price': s.get('price', {}).get('close'),
                'change_pct': s.get('price', {}).get('change_pct'),
                'score': s.get('score'),
                'recommendation': s.get('recommendation')
            }
            for s in watchlist_analysis
        ]
    }
    
    summary_file = SCRIPT_DIR / 'data' / 'analysis_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✅ 汇总已保存：{summary_file}")
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print("\n📁 查看结果:")
    print(f"  数据目录：{SCRIPT_DIR / 'data'}")
    print(f"  报告目录：{SCRIPT_DIR / 'reports'}")
    print("\n💡 提示:")
    print("  - 查看日报：ls reports/daily_*.md")
    print("  - 查看个股报告：ls reports/stock_*.md")
    print("  - 查看数据：ls data/*.csv")
    print("=" * 60)
    
    return {
        'market_data': market_data,
        'watchlist_analysis': watchlist_analysis,
        'summary': summary
    }


def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票分析系统')
    parser.add_argument('--watchlist', type=str, 
                        help='自选股代码列表，逗号分隔，如：000001,600000,000002')
    parser.add_argument('--no-save', action='store_true',
                        help='不保存文件')
    
    args = parser.parse_args()
    
    # 解析自选股
    watchlist = None
    if args.watchlist:
        watchlist = [code.strip() for code in args.watchlist.split(',')]
    
    # 运行分析
    run_full_analysis(watchlist)


if __name__ == "__main__":
    main()
