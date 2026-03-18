#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完美世界 (002624) 股票分析 - 简化版 (无需 pandas)
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Windows 控制台编码处理
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# ============ 配置 ============
DATA_DIR = Path(__file__).parent / 'data'
REPORTS_DIR = Path(__file__).parent / 'reports'
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def get_realtime_quotes(stock_code: str):
    """获取实时行情 (使用腾讯 API)"""
    # 确定市场前缀
    if stock_code.startswith('6'):
        code = f'sh{stock_code}'
    else:
        code = f'sz{stock_code}'
    
    url = f"http://qt.gtimg.cn/q={code}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'gbk'  # 腾讯返回 GBK 编码
        response.raise_for_status()
        
        # 解析返回数据
        # 格式：v_sz002624="51~完美世界~002624~12.08~11.95~12.15~..."
        text = response.text
        if '=' in text and '"' in text:
            data_part = text.split('=')[1].strip('"')
            parts = data_part.split('~')
            
            if len(parts) >= 50:
                current = float(parts[3]) if parts[3] else 0
                open_p = float(parts[5]) if parts[5] else 0
                high = float(parts[33]) if parts[33] else 0
                low = float(parts[34]) if parts[34] else 0
                prev_close = float(parts[4]) if parts[4] else 0
                volume = float(parts[6]) if parts[6] else 0
                amount = float(parts[37]) if parts[37] else 0
                
                return {
                    'code': stock_code,
                    'name': parts[1],
                    'open': open_p,
                    'high': high,
                    'low': low,
                    'close': prev_close,
                    'current': current,
                    'change': current - prev_close,
                    'change_pct': ((current - prev_close) / prev_close * 100) if prev_close else 0,
                    'volume': volume,
                    'amount': amount * 100,  # 腾讯单位是手，转换为股
                    'market_value': float(parts[45]) if len(parts) > 45 and parts[45] else 0,
                    'pe_ratio': float(parts[39]) if len(parts) > 39 and parts[39] else 0
                }
        
        print(f"⚠️ 数据格式异常：{text[:100]}")
        return None
        
    except Exception as e:
        print(f"❌ 获取行情失败：{type(e).__name__}: {e}")
        return None


def get_kline(stock_code: str, count: int = 100):
    """获取 K 线数据"""
    if stock_code.startswith('6'):
        secid = f'1.{stock_code}'
    else:
        secid = f'0.{stock_code}'
    
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        'secid': secid,
        'klt': 101,  # 日线
        'fqt': '1',  # 前复权
        'end': '20500101',
        'lmt': count,
        'fields1': 'f1,f2,f3,f4,f5,f6',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
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
        print(f"❌ 获取 K 线失败：{e}")
        return None


def calculate_ma(prices: list, period: int) -> float:
    """计算简单移动平均"""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_ema(prices: list, period: int) -> float:
    """计算指数移动平均"""
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema


def calculate_rsi(prices: list, period: int = 6) -> float:
    """计算 RSI"""
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return None
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_stock(kline_data: list) -> dict:
    """技术分析"""
    if not kline_data or len(kline_data) < 60:
        return {'error': '数据不足'}
    
    # 提取收盘价
    closes = [k['close'] for k in kline_data]
    highs = [k['high'] for k in kline_data]
    lows = [k['low'] for k in kline_data]
    volumes = [k['volume'] for k in kline_data]
    
    latest = kline_data[-1]
    prev = kline_data[-2]
    
    # 计算均线
    ma5 = calculate_ma(closes, 5)
    ma10 = calculate_ma(closes, 10)
    ma20 = calculate_ma(closes, 20)
    ma60 = calculate_ma(closes, 60)
    
    # 计算 MACD
    ema12 = calculate_ema(closes, 12)
    ema26 = calculate_ema(closes, 26)
    dif = ema12 - ema26 if ema12 and ema26 else None
    
    # 计算 RSI
    rsi6 = calculate_rsi(closes, 6)
    
    # 计算 KDJ
    lowest_9 = min(lows[-9:])
    highest_9 = max(highs[-9:])
    rsv = (latest['close'] - lowest_9) / (highest_9 - lowest_9) * 100 if highest_9 != lowest_9 else 50
    k = rsv  # 简化计算
    d = k * 0.67 + rsv * 0.33 if k else None
    j = 3 * k - 2 * d if k and d else None
    
    # 涨跌幅
    change_pct = ((latest['close'] - prev['close']) / prev['close'] * 100) if prev['close'] != 0 else 0
    
    # 信号分析
    signals = []
    
    # MA 信号
    if ma5 and ma10:
        if ma5 > ma10:
            signals.append("🟢 MA5 在 MA10 之上 (偏多)")
        else:
            signals.append("🔴 MA5 在 MA10 之下 (偏空)")
    
    # 趋势判断
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            signals.append("📈 多头排列")
        elif ma5 < ma20 < ma60:
            signals.append("📉 空头排列")
    
    # MACD 信号
    if dif:
        if dif > 0:
            signals.append("🟢 MACD 在零轴上方")
        else:
            signals.append("🔴 MACD 在零轴下方")
    
    # KDJ 信号
    if k and d:
        if k > 80 and d > 80:
            signals.append("⚠️ KDJ 超买区")
        elif k < 20 and d < 20:
            signals.append("⚠️ KDJ 超卖区")
        elif k > d:
            signals.append("🟢 KDJ 金叉")
        else:
            signals.append("🔴 KDJ 死叉")
    
    # RSI 信号
    if rsi6:
        if rsi6 > 80:
            signals.append("⚠️ RSI 超买")
        elif rsi6 < 20:
            signals.append("⚠️ RSI 超卖")
    
    # 综合评分
    score = 50
    for signal in signals:
        if '🟢' in signal or '📈' in signal:
            score += 10
        elif '🔴' in signal or '📉' in signal:
            score -= 10
        elif '超买' in signal:
            score -= 5
        elif '超卖' in signal:
            score += 5
    
    score = max(0, min(100, score))
    
    # 操作建议
    if score >= 75:
        recommendation = "🟢 强烈建议买入"
    elif score >= 60:
        recommendation = "🟢 建议买入"
    elif score >= 45:
        recommendation = "🟡 观望"
    elif score >= 30:
        recommendation = "🔴 建议减仓"
    else:
        recommendation = "🔴 强烈建议卖出"
    
    return {
        'price': {
            'open': latest['open'],
            'high': latest['high'],
            'low': latest['low'],
            'close': latest['close'],
            'change_pct': change_pct,
            'volume': latest['volume']
        },
        'indicators': {
            'MA5': round(ma5, 2) if ma5 else None,
            'MA10': round(ma10, 2) if ma10 else None,
            'MA20': round(ma20, 2) if ma20 else None,
            'MA60': round(ma60, 2) if ma60 else None,
            'DIF': round(dif, 4) if dif else None,
            'K': round(k, 2) if k else None,
            'D': round(d, 2) if d else None,
            'J': round(j, 2) if j else None,
            'RSI6': round(rsi6, 2) if rsi6 else None
        },
        'signals': signals,
        'score': score,
        'recommendation': recommendation
    }


def generate_report(stock_code: str, stock_name: str, quote: dict, analysis: dict):
    """生成报告"""
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    content = f"""# 📊 完美世界 (002624) 股票分析报告

**生成时间**: {date}

---

## 📈 实时行情

| 项目 | 数值 |
|------|------|
| 股票代码 | {stock_code} |
| 股票名称 | {stock_name} |
| 当前价 | {quote.get('f2', 'N/A')} |
| 涨跌幅 | {quote.get('f3', 'N/A')}% |
| 涨跌额 | {quote.get('f4', 'N/A')} |
| 成交量 | {quote.get('f5', 'N/A')} |
| 成交额 | {quote.get('f6', 'N/A')} |
| 今开 | {quote.get('f17', 'N/A')} |
| 最高 | {quote.get('f15', 'N/A')} |
| 最低 | {quote.get('f16', 'N/A')} |
| 昨收 | {quote.get('f18', 'N/A')} |
| 总市值 | {quote.get('f20', 'N/A')} |
| 流通市值 | {quote.get('f21', 'N/A')} |

---

## 💰 价格分析

| 项目 | 数值 |
|------|------|
| 开盘价 | {analysis['price'].get('open', 'N/A')} |
| 最高价 | {analysis['price'].get('high', 'N/A')} |
| 最低价 | {analysis['price'].get('low', 'N/A')} |
| 收盘价 | {analysis['price'].get('close', 'N/A')} |
| 涨跌幅 | {analysis['price'].get('change_pct', 'N/A'):+.2f}% |
| 成交量 | {analysis['price'].get('volume', 'N/A')} |

---

## 📉 技术指标

| 指标 | 数值 | 说明 |
|------|------|------|
| MA5 | {analysis['indicators'].get('MA5', 'N/A')} | 5 日均线 |
| MA10 | {analysis['indicators'].get('MA10', 'N/A')} | 10 日均线 |
| MA20 | {analysis['indicators'].get('MA20', 'N/A')} | 20 日均线 |
| MA60 | {analysis['indicators'].get('MA60', 'N/A')} | 60 日均线 |
| DIF | {analysis['indicators'].get('DIF', 'N/A')} | MACD 快线 |
| K | {analysis['indicators'].get('K', 'N/A')} | KDJ-K 线 |
| D | {analysis['indicators'].get('D', 'N/A')} | KDJ-D 线 |
| RSI6 | {analysis['indicators'].get('RSI6', 'N/A')} | 6 日 RSI |

---

## 🚨 交易信号

"""
    
    if analysis['signals']:
        for signal in analysis['signals']:
            content += f"- {signal}\n"
    else:
        content += "暂无明显信号\n"
    
    content += f"""

---

## 💡 综合评估

**综合评分**: {analysis['score']}/100

**操作建议**: {analysis['recommendation']}

---

## 📝 分析说明

1. **均线系统**: 观察 MA5/MA10/MA20/MA60 的排列情况判断趋势
2. **MACD**: DIF 在零轴上方为强势，下方为弱势
3. **KDJ**: 超买区 (>80) 警惕回调，超卖区 (<20) 关注反弹
4. **RSI**: >80 超买，<20 超卖

---

## ⚠️ 风险提示

- 本报告仅供参考，不构成投资建议
- 股市有风险，投资需谨慎
- 技术指标有滞后性，请结合基本面分析

---

**数据来源**: 东方财富网  
**分析系统**: 股票分析系统 v1.0 (简化版)
"""
    
    # 保存报告
    filename = f'stock_{stock_code}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    filepath = REPORTS_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return content, filepath


def main():
    """主程序"""
    stock_code = '002624'
    stock_name = '完美世界'
    
    print("""
╔══════════════════════════════════════════════════════╗
║           📊 完美世界 (002624) 股票分析               ║
║                                                      ║
║   数据源：东方财富网                                 ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 1. 获取实时行情
    print("\n[1/4] 获取实时行情...")
    quote = get_realtime_quotes(stock_code)
    
    if not quote:
        print("❌ 获取行情失败")
        return
    
    print(f"✅ {quote.get('f14', stock_name)}")
    print(f"   现价：{quote.get('f2', 'N/A')} ({quote.get('f3', 'N/A')}%)")
    
    # 2. 获取 K 线数据
    print("\n[2/4] 获取 K 线数据...")
    kline_data = get_kline(stock_code, 100)
    
    if not kline_data:
        print("❌ 获取 K 线失败")
        return
    
    print(f"✅ 获取 {len(kline_data)} 条 K 线数据")
    print(f"   最新日期：{kline_data[-1].get('date', 'N/A')}")
    
    # 3. 技术分析
    print("\n[3/4] 技术分析...")
    analysis = analyze_stock(kline_data)
    
    if 'error' in analysis:
        print(f"❌ 分析失败：{analysis['error']}")
        return
    
    print(f"\n📊 综合评分：{analysis['score']}/100")
    print(f"💡 操作建议：{analysis['recommendation']}")
    
    print(f"\n📉 技术指标:")
    for name, value in analysis['indicators'].items():
        print(f"  {name}: {value}")
    
    if analysis['signals']:
        print(f"\n🚨 交易信号:")
        for signal in analysis['signals']:
            print(f"  {signal}")
    
    # 4. 生成报告
    print("\n[4/4] 生成报告...")
    content, filepath = generate_report(stock_code, stock_name, quote, analysis)
    
    # 保存数据
    data_file = DATA_DIR / f'stock_{stock_code}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            'code': stock_code,
            'name': stock_name,
            'quote': quote,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📁 报告：{filepath}")
    print(f"📁 数据：{data_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
