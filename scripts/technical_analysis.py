#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技术分析模块 v1.0
技术指标：MA, MACD, KDJ, RSI, BOLL, VOL
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ 技术指标计算 ============
class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def MA(data: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        移动平均线 (Moving Average)
        
        Args:
            data: DataFrame，包含 'close' 列
            periods: 周期列表，默认 [5, 10, 20, 60]
        
        Returns:
            DataFrame，添加 MA 列
        """
        df = data.copy()
        for period in periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def EMA(data: pd.DataFrame, periods: List[int] = [12, 26]) -> pd.DataFrame:
        """
        指数移动平均线 (Exponential Moving Average)
        """
        df = data.copy()
        for period in periods:
            df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df
    
    @staticmethod
    def MACD(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        平滑异同移动平均线 (MACD)
        
        返回:
            MACD 线 (DIF): 快线 - 慢线
            DEA 线 (Signal): MACD 的 M 日平均
            MACD 柱 (Histogram): (DIF-DEA)*2
        """
        df = data.copy()
        
        # 计算 EMA
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        # DIF (快线)
        df['DIF'] = ema_fast - ema_slow
        
        # DEA (慢线/信号线)
        df['DEA'] = df['DIF'].ewm(span=signal, adjust=False).mean()
        
        # MACD 柱
        df['MACD'] = (df['DIF'] - df['DEA']) * 2
        
        return df
    
    @staticmethod
    def KDJ(data: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        随机指标 (KDJ)
        
        返回:
            K 线：快速确认线
            D 线：慢速主干线
            J 线：方向敏感线
        """
        df = data.copy()
        
        # 计算 N 日内最高最低价
        low_n = df['low'].rolling(window=n).min()
        high_n = df['high'].rolling(window=n).max()
        
        # 计算 RSV
        df['RSV'] = (df['close'] - low_n) / (high_n - low_n) * 100
        
        # 计算 K 线 (RSV 的 M1 日移动平均)
        df['K'] = df['RSV'].ewm(com=m1-1, adjust=False).mean()
        
        # 计算 D 线 (K 的 M2 日移动平均)
        df['D'] = df['K'].ewm(com=m2-1, adjust=False).mean()
        
        # 计算 J 线 (3K - 2D)
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        return df
    
    @staticmethod
    def RSI(data: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """
        相对强弱指标 (RSI)
        
        RSI > 80: 超买
        RSI < 20: 超卖
        """
        df = data.copy()
        
        for period in periods:
            # 计算价格变化
            delta = df['close'].diff()
            
            # 分离涨跌
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # 计算平均涨跌
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # 计算 RS 和 RSI
            rs = avg_gain / avg_loss
            df[f'RSI{period}'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def BOLL(data: pd.DataFrame, period: int = 20, width: float = 2.0) -> pd.DataFrame:
        """
        布林带 (Bollinger Bands)
        
        返回:
            UPPER: 上轨 (中轨 + 2 倍标准差)
            MID: 中轨 (20 日均线)
            LOWER: 下轨 (中轨 - 2 倍标准差)
        """
        df = data.copy()
        
        # 中轨
        df['BOLL_MID'] = df['close'].rolling(window=period).mean()
        
        # 标准差
        std = df['close'].rolling(window=period).std()
        
        # 上下轨
        df['BOLL_UPPER'] = df['BOLL_MID'] + width * std
        df['BOLL_LOWER'] = df['BOLL_MID'] - width * std
        
        return df
    
    @staticmethod
    def VOL_MA(data: pd.DataFrame, periods: List[int] = [5, 10]) -> pd.DataFrame:
        """
        成交量均线
        """
        df = data.copy()
        for period in periods:
            df[f'VOL_MA{period}'] = df['volume'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def ATR(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        平均真实波幅 (Average True Range) - 波动率指标
        """
        df = data.copy()
        
        # 计算 TR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # ATR
        df['ATR'] = tr.rolling(window=period).mean()
        
        return df
    
    @staticmethod
    def calculate_all(data: pd.DataFrame) -> pd.DataFrame:
        """
        一次性计算所有指标
        """
        df = data.copy()
        
        # 均线
        df = TechnicalIndicators.MA(df, [5, 10, 20, 60])
        df = TechnicalIndicators.EMA(df, [12, 26])
        
        # MACD
        df = TechnicalIndicators.MACD(df)
        
        # KDJ
        df = TechnicalIndicators.KDJ(df)
        
        # RSI
        df = TechnicalIndicators.RSI(df, [6, 12, 24])
        
        # BOLL
        df = TechnicalIndicators.BOLL(df)
        
        # 成交量均线
        df = TechnicalIndicators.VOL_MA(df, [5, 10])
        
        # ATR
        df = TechnicalIndicators.ATR(df)
        
        return df


# ============ 信号分析 ============
class SignalAnalyzer:
    """交易信号分析器"""
    
    @staticmethod
    def analyze_ma_signal(df: pd.DataFrame) -> Optional[str]:
        """
        均线信号分析
        """
        if len(df) < 60:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 金叉：短周期上穿长周期
        if latest['MA5'] > latest['MA10'] and prev['MA5'] <= prev['MA10']:
            return "🟢 MA 金叉 (5 日上穿 10 日)"
        
        # 死叉：短周期下穿长周期
        if latest['MA5'] < latest['MA10'] and prev['MA5'] >= prev['MA10']:
            return "🔴 MA 死叉 (5 日下穿 10 日)"
        
        # 多头排列
        if (latest['MA5'] > latest['MA10'] > latest['MA20'] > latest['MA60']):
            return "📈 多头排列"
        
        # 空头排列
        if (latest['MA5'] < latest['MA10'] < latest['MA20'] < latest['MA60']):
            return "📉 空头排列"
        
        return None
    
    @staticmethod
    def analyze_macd_signal(df: pd.DataFrame) -> Optional[str]:
        """
        MACD 信号分析
        """
        if len(df) < 30:
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 金叉
        if latest['DIF'] > latest['DEA'] and prev['DIF'] <= prev['DEA']:
            return "🟢 MACD 金叉"
        
        # 死叉
        if latest['DIF'] < latest['DEA'] and prev['DIF'] >= prev['DEA']:
            return "🔴 MACD 死叉"
        
        # 底背离
        if latest['MACD'] > 0 and prev['MACD'] <= 0:
            return "🟢 MACD 翻红"
        
        # 顶背离
        if latest['MACD'] < 0 and prev['MACD'] >= 0:
            return "🔴 MACD 翻绿"
        
        return None
    
    @staticmethod
    def analyze_kdj_signal(df: pd.DataFrame) -> Optional[str]:
        """
        KDJ 信号分析
        """
        if len(df) < 20:
            return None
        
        latest = df.iloc[-1]
        
        k = latest.get('K', 50)
        d = latest.get('D', 50)
        j = latest.get('J', 50)
        
        # 超买
        if k > 80 and d > 80:
            return "⚠️ KDJ 超买区 (K>80, D>80)"
        
        # 超卖
        if k < 20 and d < 20:
            return "⚠️ KDJ 超卖区 (K<20, D<20)"
        
        # 金叉
        if k > d and df.iloc[-2]['K'] <= df.iloc[-2]['D']:
            return "🟢 KDJ 金叉"
        
        # 死叉
        if k < d and df.iloc[-2]['K'] >= df.iloc[-2]['D']:
            return "🔴 KDJ 死叉"
        
        return None
    
    @staticmethod
    def analyze_rsi_signal(df: pd.DataFrame) -> Optional[str]:
        """
        RSI 信号分析
        """
        if len(df) < 30:
            return None
        
        latest = df.iloc[-1]
        rsi6 = latest.get('RSI6', 50)
        rsi12 = latest.get('RSI12', 50)
        rsi24 = latest.get('RSI24', 50)
        
        # 超买
        if rsi6 > 80:
            return "⚠️ RSI 超买 (RSI6>80)"
        
        # 超卖
        if rsi6 < 20:
            return "⚠️ RSI 超卖 (RSI6<20)"
        
        return None
    
    @staticmethod
    def analyze_boll_signal(df: pd.DataFrame) -> Optional[str]:
        """
        布林带信号分析
        """
        if len(df) < 30:
            return None
        
        latest = df.iloc[-1]
        close = latest['close']
        upper = latest.get('BOLL_UPPER', 0)
        lower = latest.get('BOLL_LOWER', 0)
        mid = latest.get('BOLL_MID', 0)
        
        # 触上轨
        if close >= upper * 0.99:
            return "⚠️ 触及布林上轨 (可能回调)"
        
        # 触下轨
        if close <= lower * 1.01:
            return "⚠️ 触及布林下轨 (可能反弹)"
        
        # 突破中轨
        if close > mid and df.iloc[-2]['close'] <= df.iloc[-2].get('BOLL_MID', close):
            return "🟢 突破布林中轨"
        
        if close < mid and df.iloc[-2]['close'] >= df.iloc[-2].get('BOLL_MID', close):
            return "🔴 跌破布林中轨"
        
        return None
    
    @staticmethod
    def get_all_signals(df: pd.DataFrame) -> List[Dict]:
        """
        获取所有信号
        """
        signals = []
        
        analyzers = [
            ('MA', SignalAnalyzer.analyze_ma_signal),
            ('MACD', SignalAnalyzer.analyze_macd_signal),
            ('KDJ', SignalAnalyzer.analyze_kdj_signal),
            ('RSI', SignalAnalyzer.analyze_rsi_signal),
            ('BOLL', SignalAnalyzer.analyze_boll_signal),
        ]
        
        for name, analyzer in analyzers:
            signal = analyzer(df)
            if signal:
                signals.append({
                    'type': name,
                    'signal': signal,
                    'timestamp': df.iloc[-1].get('date', '')
                })
        
        return signals


# ============ 股票分析主类 ============
class StockAnalyzer:
    """股票分析器"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.signal_analyzer = SignalAnalyzer()
    
    def analyze_stock(self, kline_data: List[Dict]) -> Dict:
        """
        分析单只股票
        
        Args:
            kline_data: K 线数据列表
        
        Returns:
            分析结果字典
        """
        if not kline_data:
            return {'error': '无数据'}
        
        # 转换为 DataFrame
        df = pd.DataFrame(kline_data)
        
        # 确保有必要的列
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                return {'error': f'缺少必要列：{col}'}
        
        # 计算所有指标
        df = TechnicalIndicators.calculate_all(df)
        
        # 获取最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # 计算涨跌幅
        change_pct = ((latest['close'] - prev['close']) / prev['close'] * 100) if prev['close'] != 0 else 0
        
        # 获取所有信号
        signals = self.signal_analyzer.get_all_signals(df)
        
        # 综合评分
        score = self._calculate_score(df, signals)
        
        result = {
            'timestamp': latest.get('date', ''),
            'price': {
                'open': round(latest['open'], 2),
                'high': round(latest['high'], 2),
                'low': round(latest['low'], 2),
                'close': round(latest['close'], 2),
                'change_pct': round(change_pct, 2),
                'volume': round(latest['volume'], 2)
            },
            'indicators': {
                'MA5': round(latest.get('MA5', 0), 2),
                'MA10': round(latest.get('MA10', 0), 2),
                'MA20': round(latest.get('MA20', 0), 2),
                'MA60': round(latest.get('MA60', 0), 2),
                'DIF': round(latest.get('DIF', 0), 4),
                'DEA': round(latest.get('DEA', 0), 4),
                'K': round(latest.get('K', 0), 2),
                'D': round(latest.get('D', 0), 2),
                'J': round(latest.get('J', 0), 2),
                'RSI6': round(latest.get('RSI6', 0), 2),
                'BOLL_UPPER': round(latest.get('BOLL_UPPER', 0), 2),
                'BOLL_MID': round(latest.get('BOLL_MID', 0), 2),
                'BOLL_LOWER': round(latest.get('BOLL_LOWER', 0), 2),
            },
            'signals': signals,
            'score': score,
            'recommendation': self._get_recommendation(score, signals)
        }
        
        return result
    
    def _calculate_score(self, df: pd.DataFrame, signals: List[Dict]) -> int:
        """
        计算综合评分 (0-100)
        """
        score = 50  # 基础分
        
        # 信号加分/减分
        for signal in signals:
            if '🟢' in signal['signal']:
                score += 10
            elif '🔴' in signal['signal']:
                score -= 10
            elif '📈' in signal['signal']:
                score += 15
            elif '📉' in signal['signal']:
                score -= 15
            elif '超买' in signal['signal']:
                score -= 5
            elif '超卖' in signal['signal']:
                score += 5
        
        # 趋势加分
        if df.iloc[-1]['close'] > df.iloc[-1].get('MA20', 0):
            score += 5
        else:
            score -= 5
        
        # 限制在 0-100
        return max(0, min(100, score))
    
    def _get_recommendation(self, score: int, signals: List[Dict]) -> str:
        """
        获取操作建议
        """
        if score >= 75:
            return "🟢 强烈建议买入"
        elif score >= 60:
            return "🟢 建议买入"
        elif score >= 45:
            return "🟡 观望"
        elif score >= 30:
            return "🔴 建议减仓"
        else:
            return "🔴 强烈建议卖出"


# ============ 主程序 ============
def main():
    """主程序 - 示例"""
    from stock_collector import EastMoneyAPI
    
    print("""
╔══════════════════════════════════════════════════════╗
║           📊 股票技术分析系统 v1.0                    ║
║                                                      ║
║   指标：MA, MACD, KDJ, RSI, BOLL, ATR                ║
║   信号：金叉/死叉，超买/超卖，突破                     ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 采集数据
    print("\n[1/3] 采集股票数据...")
    api = EastMoneyAPI()
    kline_data = api.get_kline('000001', 'day', 100)
    
    if not kline_data:
        print("❌ 数据获取失败")
        return
    
    # 技术分析
    print("\n[2/3] 计算技术指标...")
    analyzer = StockAnalyzer()
    result = analyzer.analyze_stock(kline_data)
    
    # 显示结果
    print("\n[3/3] 分析结果:")
    print("=" * 60)
    print(f"📈 平安银行 (000001)")
    print(f"📅 日期：{result['timestamp']}")
    print(f"💰 价格：{result['price']['close']} ({result['price']['change_pct']:+.2f}%)")
    print(f"📊 评分：{result['score']}/100")
    print(f"💡 建议：{result['recommendation']}")
    
    print("\n📉 技术指标:")
    for name, value in result['indicators'].items():
        print(f"  {name}: {value}")
    
    if result['signals']:
        print("\n🚨 交易信号:")
        for signal in result['signals']:
            print(f"  {signal['type']}: {signal['signal']}")
    
    print("=" * 60)
    print("✅ 分析完成！")


if __name__ == "__main__":
    main()
