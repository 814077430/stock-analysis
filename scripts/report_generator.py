#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票报告生成系统 v1.0
报告类型：日报、个股分析、周报
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ 配置 ============
REPORTS_DIR = Path(__file__).parent / 'reports'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = Path(__file__).parent / 'data'


# ============ 报告模板 ============
class ReportTemplates:
    """报告模板"""
    
    @staticmethod
    def daily_report_header(date: str) -> str:
        return f"""# 📈 股市日报

**日期**: {date}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**市场**: A 股 (上证/深证/北交所)

---

## 📊 市场概览

"""
    
    @staticmethod
    def market_summary(data: Dict) -> str:
        return f"""### 市场统计

| 市场 | 股票数量 | 上涨 | 下跌 | 平盘 |
|------|----------|------|------|------|
| 上证 | {data.get('sh_count', 0)} | - | - | - |
| 深证 | {data.get('sz_count', 0)} | - | - | - |
| 北交所 | {data.get('bj_count', 0)} | - | - | - |
| **合计** | **{data.get('total_stocks', 0)}** | - | - | - |

---

"""
    
    @staticmethod
    def stock_analysis(stock_data: Dict) -> str:
        """个股分析模板"""
        code = stock_data.get('code', 'Unknown')
        name = stock_data.get('name', 'Unknown')
        price = stock_data.get('price', {})
        indicators = stock_data.get('indicators', {})
        signals = stock_data.get('signals', [])
        score = stock_data.get('score', 50)
        recommendation = stock_data.get('recommendation', '观望')
        
        content = f"""### {name} ({code})

**综合评分**: {score}/100  
**操作建议**: {recommendation}

#### 价格信息

| 项目 | 数值 |
|------|------|
| 开盘 | {price.get('open', 'N/A')} |
| 最高 | {price.get('high', 'N/A')} |
| 最低 | {price.get('low', 'N/A')} |
| 收盘 | {price.get('close', 'N/A')} |
| 涨跌幅 | {price.get('change_pct', 'N/A'):+.2f}% |
| 成交量 | {price.get('volume', 'N/A')} |

#### 技术指标

| 指标 | 数值 | 指标 | 数值 |
|------|------|------|------|
| MA5 | {indicators.get('MA5', 'N/A')} | MA20 | {indicators.get('MA20', 'N/A')} |
| MA10 | {indicators.get('MA10', 'N/A')} | MA60 | {indicators.get('MA60', 'N/A')} |
| DIF | {indicators.get('DIF', 'N/A')} | DEA | {indicators.get('DEA', 'N/A')} |
| K | {indicators.get('K', 'N/A')} | D | {indicators.get('D', 'N/A')} |
| RSI6 | {indicators.get('RSI6', 'N/A')} | - | - |

#### 交易信号

"""
        
        if signals:
            for signal in signals:
                content += f"- {signal['signal']}\n"
        else:
            content += "暂无明显信号\n"
        
        content += "\n---\n\n"
        return content
    
    @staticmethod
    def watchlist_summary(watchlist: List[Dict]) -> str:
        """自选股汇总"""
        content = """## 📋 自选股表现

| 代码 | 名称 | 现价 | 涨跌幅 | 评分 | 建议 |
|------|------|------|--------|------|------|
"""
        
        for stock in watchlist:
            code = stock.get('code', 'N/A')
            name = stock.get('name', 'N/A')
            price = stock.get('price', {}).get('close', 'N/A')
            change = stock.get('price', {}).get('change_pct', 0)
            score = stock.get('score', 50)
            rec = stock.get('recommendation', '观望')
            
            # 涨跌幅颜色
            change_str = f"{change:+.2f}%"
            
            content += f"| {code} | {name} | {price} | {change_str} | {score} | {rec} |\n"
        
        content += "\n---\n\n"
        return content
    
    @staticmethod
    def top_gainers(gainers: List[Dict]) -> str:
        """涨幅榜"""
        content = """## 🚀 涨幅榜 (Top 10)

| 排名 | 代码 | 名称 | 现价 | 涨跌幅 |
|------|------|------|------|--------|
"""
        
        for i, stock in enumerate(gainers[:10], 1):
            code = stock.get('code', 'N/A')
            name = stock.get('name', 'N/A')
            price = stock.get('price', {}).get('close', 'N/A')
            change = stock.get('price', {}).get('change_pct', 0)
            
            content += f"| {i} | {code} | {name} | {price} | {change:+.2f}% |\n"
        
        content += "\n---\n\n"
        return content
    
    @staticmethod
    def top_losers(losers: List[Dict]) -> str:
        """跌幅榜"""
        content = """## 📉 跌幅榜 (Top 10)

| 排名 | 代码 | 名称 | 现价 | 涨跌幅 |
|------|------|------|------|--------|
"""
        
        for i, stock in enumerate(losers[:10], 1):
            code = stock.get('code', 'N/A')
            name = stock.get('name', 'N/A')
            price = stock.get('price', {}).get('close', 'N/A')
            change = stock.get('price', {}).get('change_pct', 0)
            
            content += f"| {i} | {code} | {name} | {price} | {change:+.2f}% |\n"
        
        content += "\n---\n\n"
        return content
    
    @staticmethod
    def footer() -> str:
        return """---

## 📝 免责声明

本报告由自动生成系统创建，仅供参考，不构成投资建议。

股市有风险，投资需谨慎。

---

**生成系统**: 股票分析系统 v1.0  
**数据源**: 东方财富、新浪财经
"""


# ============ 报告生成器 ============
class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.templates = ReportTemplates()
    
    def generate_daily_report(self, market_data: Dict, 
                              watchlist_analysis: List[Dict],
                              top_gainers: List[Dict] = None,
                              top_losers: List[Dict] = None,
                              save: bool = True) -> str:
        """
        生成日报
        
        Args:
            market_data: 市场数据
            watchlist_analysis: 自选股分析结果
            top_gainers: 涨幅榜
            top_losers: 跌幅榜
            save: 是否保存文件
        
        Returns:
            报告内容
        """
        date = datetime.now().strftime('%Y-%m-%d')
        
        content = self.templates.daily_report_header(date)
        content += self.templates.market_summary(market_data)
        
        if top_gainers:
            content += self.templates.top_gainers(top_gainers)
        
        if top_losers:
            content += self.templates.top_losers(top_losers)
        
        if watchlist_analysis:
            content += self.templates.watchlist_summary(watchlist_analysis)
        
        # 详细分析 (前 5 只)
        content += "## 🔍 个股详细分析\n\n"
        for stock in watchlist_analysis[:5]:
            content += self.templates.stock_analysis(stock)
        
        content += self.templates.footer()
        
        if save:
            filename = f'daily_report_{date.replace("-", "")}.md'
            filepath = REPORTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ 日报已保存：{filepath}")
        
        return content
    
    def generate_stock_report(self, stock_data: Dict, save: bool = True) -> str:
        """
        生成个股分析报告
        
        Args:
            stock_data: 股票分析数据
            save: 是否保存文件
        
        Returns:
            报告内容
        """
        code = stock_data.get('code', 'Unknown')
        date = datetime.now().strftime('%Y-%m-%d')
        
        content = f"""# 📊 个股分析报告

**股票代码**: {code}  
**报告日期**: {date}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        content += self.templates.stock_analysis(stock_data)
        
        # 历史走势分析
        content += """## 📈 历史走势分析

### 近期表现

| 周期 | 涨跌幅 | 均线位置 |
|------|--------|----------|
| 5 日 | - | - |
| 10 日 | - | - |
| 20 日 | - | - |
| 60 日 | - | - |

### 技术形态

- **均线系统**: 待分析
- **MACD**: 待分析
- **KDJ**: 待分析
- **RSI**: 待分析
- **布林带**: 待分析

---

## 💡 操作建议

根据综合分析，给出以下建议：

1. **短期** (1-5 天): 待分析
2. **中期** (1-4 周): 待分析
3. **长期** (1-3 月): 待分析

---

## ⚠️ 风险提示

- 市场风险
- 行业风险
- 公司经营风险
- 政策风险

---

"""
        content += self.templates.footer()
        
        if save:
            filename = f'stock_{code}_report_{date.replace("-", "")}.md'
            filepath = REPORTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ 个股报告已保存：{filepath}")
        
        return content
    
    def generate_weekly_report(self, weekly_data: Dict, save: bool = True) -> str:
        """
        生成周报
        
        Args:
            weekly_data: 周度数据汇总
            save: 是否保存文件
        """
        week_start = datetime.now() - timedelta(days=7)
        date_range = f"{week_start.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}"
        
        content = f"""# 📈 股市周报

**周期**: {date_range}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 本周市场回顾

### 主要指数表现

| 指数 | 周一开盘 | 周五收盘 | 周涨跌 | 周振幅 |
|------|----------|----------|--------|--------|
| 上证指数 | - | - | - | - |
| 深证成指 | - | - | - | - |
| 创业板指 | - | - | - | - |

### 市场统计

| 指标 | 数值 |
|------|------|
| 总成交额 | - |
| 上涨股票数 | - |
| 下跌股票数 | - |
| 涨停股票数 | - |
| 跌停股票数 | - |

---

## 🔥 本周热点

### 领涨板块

| 排名 | 板块 | 周涨幅 |
|------|------|--------|
| 1 | - | - |
| 2 | - | - |
| 3 | - | - |

### 热门股票

| 排名 | 代码 | 名称 | 周涨幅 |
|------|------|------|--------|
| 1 | - | - | - |
| 2 | - | - | - |
| 3 | - | - | - |

---

## 📋 自选股本周表现

待填充...

---

## 💡 下周展望

### 关注要点

1. 宏观经济数据
2. 政策面变化
3. 资金面情况
4. 外围市场

### 操作策略

- **仓位建议**: 待分析
- **关注板块**: 待分析
- **风险提示**: 待分析

---

"""
        content += self.templates.footer()
        
        if save:
            filename = f'weekly_report_{datetime.now().strftime("%Y%m%d")}.md'
            filepath = REPORTS_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ 周报已保存：{filepath}")
        
        return content


# ============ 主程序 ============
def main():
    """主程序 - 示例"""
    print("""
╔══════════════════════════════════════════════════════╗
║           📄 股票报告生成系统 v1.0                    ║
║                                                      ║
║   报告类型：日报、个股分析、周报                      ║
║   输出目录：./reports/                                ║
╚══════════════════════════════════════════════════════╝
    """)
    
    generator = ReportGenerator()
    
    # 示例数据
    market_data = {
        'total_stocks': 5000,
        'sh_count': 2000,
        'sz_count': 2500,
        'bj_count': 500
    }
    
    watchlist = [
        {
            'code': '000001',
            'name': '平安银行',
            'price': {'close': 10.5, 'change_pct': 1.5, 'open': 10.3, 'high': 10.6, 'low': 10.2, 'volume': 1000000},
            'score': 72,
            'recommendation': '建议买入',
            'indicators': {'MA5': 10.2, 'MA10': 10.0, 'MA20': 9.8, 'MA60': 9.5, 'DIF': 0.15, 'DEA': 0.12, 'K': 65, 'D': 60, 'RSI6': 58},
            'signals': [{'signal': '🟢 MACD 金叉', 'type': 'MACD'}]
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'price': {'close': 8.2, 'change_pct': -0.5, 'open': 8.3, 'high': 8.4, 'low': 8.1, 'volume': 800000},
            'score': 45,
            'recommendation': '观望',
            'indicators': {'MA5': 8.3, 'MA10': 8.4, 'MA20': 8.5, 'MA60': 8.6, 'DIF': -0.05, 'DEA': -0.03, 'K': 40, 'D': 45, 'RSI6': 42},
            'signals': [{'signal': '🔴 KDJ 死叉', 'type': 'KDJ'}]
        }
    ]
    
    # 生成日报
    print("\n[1/2] 生成日报...")
    daily = generator.generate_daily_report(
        market_data=market_data,
        watchlist_analysis=watchlist,
        save=True
    )
    
    # 生成个股报告
    print("\n[2/2] 生成个股报告...")
    stock_report = generator.generate_stock_report(watchlist[0], save=True)
    
    print("\n" + "=" * 60)
    print("✅ 报告生成完成！查看 ./reports/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
