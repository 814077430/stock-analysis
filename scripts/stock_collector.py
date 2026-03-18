#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集模块 v1.0
数据源：东方财富、新浪财经、腾讯财经
"""

import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ 配置 ============
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============ 工具函数 ============
def get_headers() -> Dict:
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'http://quote.eastmoney.com/'
    }

def save_to_csv(data: List[Dict], filename: str):
    """保存数据到 CSV"""
    if not data:
        logger.warning("数据为空，跳过保存")
        return
    
    df = pd.DataFrame(data)
    filepath = DATA_DIR / filename
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    logger.info(f"✅ 数据已保存：{filepath}")

def save_to_json(data: Dict, filename: str):
    """保存数据到 JSON"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 数据已保存：{filepath}")


# ============ 东方财富数据源 ============
class EastMoneyAPI:
    """东方财富 API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_headers())
    
    def get_stock_list(self, market: str = 'sh') -> List[Dict]:
        """
        获取股票列表
        market: sh-上证，sz-深证，bj-北交所
        """
        url = f"http://{market}.push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': '1',
            'pz': '500',  # 每页数量
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f3',
            'fs': f'm:{1 if market == "sh" else 0} t:{2 if market == "sh" else 1}',
            'fields': 'f12,f14,f2,f3,f4,f5,f6,f8,f13,f17,f18,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                stocks = data['data']['diff']
                logger.info(f"✅ 获取 {market.upper()} 股票列表：{len(stocks)} 只")
                return stocks
            else:
                logger.warning(f"⚠️ 未获取到 {market.upper()} 股票数据")
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取股票列表失败：{e}")
            return []
    
    def get_realtime_quotes(self, stock_codes: List[str]) -> List[Dict]:
        """
        获取实时行情
        stock_codes: 股票代码列表，如 ['000001', '600000']
        """
        if not stock_codes:
            return []
        
        # 添加市场前缀
        codes = []
        for code in stock_codes:
            if code.startswith('6'):
                codes.append(f'sh{code}')
            else:
                codes.append(f'sz{code}')
        
        url = "http://push2.eastmoney.com/api/qt/ulist.nav/get"
        params = {
            'secids': ','.join(codes),
            'fields': 'f12,f14,f2,f3,f4,f5,f6,f8,f9,f10,f13,f17,f18,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('diff'):
                quotes = data['data']['diff']
                logger.info(f"✅ 获取实时行情：{len(quotes)} 只")
                return quotes
            else:
                logger.warning("⚠️ 未获取到实时行情数据")
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取实时行情失败：{e}")
            return []
    
    def get_kline(self, stock_code: str, period: str = 'day', count: int = 100) -> List[Dict]:
        """
        获取 K 线数据
        stock_code: 股票代码
        period: day-日线，week-周线，month-月线，1m-1 分钟，5m-5 分钟，15m-15 分钟，30m-30 分钟，60m-60 分钟
        count: 获取数量
        """
        # 确定市场
        if stock_code.startswith('6'):
            secid = f'1.{stock_code}'
        else:
            secid = f'0.{stock_code}'
        
        # 周期映射
        period_map = {
            'day': 101, 'week': 102, 'month': 103,
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '60m': 60
        }
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            'secid': secid,
            'klt': period_map.get(period, 101),
            'fqt': '1',  # 前复权
            'end': '20500101',
            'lmt': count,
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and data['data'].get('klines'):
                klines = data['data']['klines']
                # 解析 K 线数据
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
                logger.info(f"✅ 获取 K 线数据：{stock_code} {len(result)} 条")
                return result
            else:
                logger.warning(f"⚠️ 未获取到 K 线数据：{stock_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ 获取 K 线数据失败：{e}")
            return []
    
    def get_stock_info(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        if stock_code.startswith('6'):
            secid = f'1.{stock_code}'
        else:
            secid = f'0.{stock_code}'
        
        url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': secid,
            'fields': 'f12,f14,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                info = data['data']
                logger.info(f"✅ 获取股票信息：{info.get('f14', 'Unknown')}")
                return info
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取股票信息失败：{e}")
            return None


# ============ 新浪财经数据源 ============
class SinaAPI:
    """新浪财经 API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_headers())
    
    def get_realtime_quotes(self, stock_codes: List[str]) -> List[Dict]:
        """
        获取实时行情 (新浪)
        返回字段更丰富，包含买卖盘口
        """
        if not stock_codes:
            return []
        
        # 添加市场前缀
        codes = []
        for code in stock_codes:
            if code.startswith('6'):
                codes.append(f'sh{code}')
            else:
                codes.append(f'sz{code}')
        
        url = "http://hq.sinajs.cn/list=" + ','.join(codes)
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'  # 新浪返回 GBK 编码
            response.raise_for_status()
            
            result = []
            for line in response.text.split('\n'):
                if '=' in line:
                    parts = line.split('=')
                    if len(parts) == 2 and parts[1].strip():
                        code = parts[0].split('_')[-1]
                        data = parts[1].strip('"').split(',')
                        if len(data) >= 32:
                            result.append({
                                'code': code,
                                'name': data[0],
                                'open': float(data[1]),
                                'high': float(data[2]),
                                'low': float(data[3]),
                                'close': float(data[4]),  # 昨收
                                'current': float(data[31]),  # 现价
                                'volume': float(data[8]),
                                'amount': float(data[9]),
                                'bid1': float(data[11]),
                                'bid1_vol': float(data[10]),
                                'ask1': float(data[13]),
                                'ask1_vol': float(data[12]),
                                'bid2': float(data[15]),
                                'bid2_vol': float(data[14]),
                                'ask2': float(data[17]),
                                'ask2_vol': float(data[16]),
                                'bid3': float(data[19]),
                                'bid3_vol': float(data[18]),
                                'ask3': float(data[21]),
                                'ask3_vol': float(data[20]),
                                'bid4': float(data[23]),
                                'bid4_vol': float(data[22]),
                                'ask4': float(data[25]),
                                'ask4_vol': float(data[24]),
                                'bid5': float(data[27]),
                                'bid5_vol': float(data[26]),
                                'ask5': float(data[29]),
                                'ask5_vol': float(data[28]),
                                'date': data[30],
                                'time': data[31]
                            })
            
            logger.info(f"✅ 获取新浪实时行情：{len(result)} 只")
            return result
            
        except Exception as e:
            logger.error(f"❌ 获取新浪行情失败：{e}")
            return []


# ============ 数据采集主类 ============
class StockDataCollector:
    """股票数据采集器"""
    
    def __init__(self):
        self.eastmoney = EastMoneyAPI()
        self.sina = SinaAPI()
    
    def collect_all_stocks(self, save: bool = True) -> Dict:
        """采集全市场股票数据"""
        logger.info("🚀 开始采集全市场股票数据...")
        
        # 获取股票列表
        sh_stocks = self.eastmoney.get_stock_list('sh')
        sz_stocks = self.eastmoney.get_stock_list('sz')
        bj_stocks = self.eastmoney.get_stock_list('bj')
        
        all_stocks = sh_stocks + sz_stocks + bj_stocks
        
        logger.info(f"📊 全市场股票总数：{len(all_stocks)} 只")
        
        # 保存股票列表
        if save and all_stocks:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_to_csv(all_stocks, f'stock_list_{timestamp}.csv')
        
        # 获取实时行情
        stock_codes = [s.get('f12', '') for s in all_stocks if s.get('f12')]
        quotes = self.eastmoney.get_realtime_quotes(stock_codes[:500])  # 限制数量避免超时
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_stocks': len(all_stocks),
            'sh_count': len(sh_stocks),
            'sz_count': len(sz_stocks),
            'bj_count': len(bj_stocks),
            'quotes': quotes
        }
        
        if save:
            save_to_json(result, f'market_snapshot_{timestamp}.json')
        
        return result
    
    def collect_stock_detail(self, stock_code: str, save: bool = True) -> Dict:
        """采集单只股票详细数据"""
        logger.info(f"🔍 采集股票详情：{stock_code}")
        
        # 基本信息
        info = self.eastmoney.get_stock_info(stock_code)
        
        # K 线数据
        kline_day = self.eastmoney.get_kline(stock_code, 'day', 100)
        kline_week = self.eastmoney.get_kline(stock_code, 'week', 52)
        
        # 实时行情
        quotes = self.eastmoney.get_realtime_quotes([stock_code])
        
        result = {
            'code': stock_code,
            'timestamp': datetime.now().isoformat(),
            'info': info,
            'kline_day': kline_day,
            'kline_week': kline_week,
            'quote': quotes[0] if quotes else None
        }
        
        if save:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_to_json(result, f'stock_{stock_code}_{timestamp}.json')
            if kline_day:
                save_to_csv(kline_day, f'stock_{stock_code}_kline.csv')
        
        return result
    
    def collect_watchlist(self, watchlist: List[str], save: bool = True) -> List[Dict]:
        """采集自选股数据"""
        logger.info(f"📋 采集自选股：{len(watchlist)} 只")
        
        quotes = self.eastmoney.get_realtime_quotes(watchlist)
        
        if save and quotes:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_to_csv(quotes, f'watchlist_{timestamp}.csv')
        
        return quotes


# ============ 主程序 ============
def main():
    """主程序"""
    collector = StockDataCollector()
    
    print("""
╔══════════════════════════════════════════════════════╗
║           📈 股票数据采集系统 v1.0                    ║
║                                                      ║
║   数据源：东方财富、新浪财经                          ║
║   数据目录：./data/                                   ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 示例：采集全市场数据
    print("\n[1/3] 采集全市场股票列表...")
    market_data = collector.collect_all_stocks(save=True)
    print(f"  ✅ 全市场股票：{market_data['total_stocks']} 只")
    print(f"     - 上证：{market_data['sh_count']} 只")
    print(f"     - 深证：{market_data['sz_count']} 只")
    print(f"     - 北交所：{market_data['bj_count']} 只")
    
    # 示例：采集单只股票
    print("\n[2/3] 采集单只股票详情 (示例：000001)...")
    stock_data = collector.collect_stock_detail('000001', save=True)
    if stock_data['quote']:
        print(f"  ✅ 平安银行")
        print(f"     现价：{stock_data['quote'].get('f2', 'N/A')}")
        print(f"     涨跌幅：{stock_data['quote'].get('f3', 'N/A')}%")
    
    # 示例：采集自选股
    print("\n[3/3] 采集自选股 (示例)...")
    watchlist = ['000001', '600000', '000002', '600519']
    watch_data = collector.collect_watchlist(watchlist, save=True)
    print(f"  ✅ 采集 {len(watch_data)} 只自选股")
    
    print("\n" + "=" * 60)
    print("✅ 数据采集完成！查看 ./data/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
