# 📈 股票分析系统 v1.0 - 项目文档

---

## 📁 项目结构

```
stock_analysis/
├── scripts/
│   ├── main.py                 # 主程序
│   ├── stock_collector.py      # 数据采集
│   ├── technical_analysis.py   # 技术分析
│   └── report_generator.py     # 报告生成
├── data/                       # 数据目录
├── reports/                    # 报告目录
├── requirements.txt
├── run_analysis.bat
└── README.md
```

---

## 🔧 核心模块

### 1. 数据采集 (`stock_collector.py`)

**数据源**: 腾讯财经、东方财富

**功能**:
- 实时行情
- K 线数据 (日线/周线/月线)
- 全市场股票列表
- 自选股监控

**使用示例**:
```python
from stock_collector import StockDataCollector

collector = StockDataCollector()

# 实时行情
quotes = collector.get_realtime_quotes(['000001', '600000'])

# K 线数据
kline = collector.get_kline('000001', 'day', 100)

# 保存数据
collector.save_to_csv(kline, 'stock_000001.csv')
```

---

### 2. 技术分析 (`technical_analysis.py`)

**技术指标**:
| 指标 | 说明 |
|------|------|
| MA | 移动平均线 (5/10/20/60 日) |
| MACD | 平滑异同移动平均 |
| KDJ | 随机指标 |
| RSI | 相对强弱指标 |
| BOLL | 布林带 |

**使用示例**:
```python
from technical_analysis import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze_stock(kline_data)

print(f"评分：{result['score']}/100")
print(f"建议：{result['recommendation']}")
```

---

### 3. 报告生成 (`report_generator.py`)

**报告类型**:
- 每日复盘报告
- 个股分析报告

**使用示例**:
```python
from report_generator import ReportGenerator

generator = ReportGenerator()

# 生成日报
generator.generate_daily_report(market_data, watchlist)

# 生成个股报告
generator.generate_stock_report(stock_data)
```

---

## 📊 数据字段

### K 线数据
| 字段 | 说明 |
|------|------|
| date | 日期 |
| open | 开盘价 |
| close | 收盘价 |
| high | 最高价 |
| low | 最低价 |
| volume | 成交量 |

### 技术指标
| 字段 | 说明 |
|------|------|
| MA5/10/20/60 | 均线 |
| DIF/DEA | MACD 线 |
| K/D/J | KDJ 线 |
| RSI6 | 6 日 RSI |

---

## 🛠️ 扩展开发

### 添加新数据源
```python
class NewDataSource:
    def get_quote(self, code):
        # 实现数据抓取
        pass
```

### 添加新指标
```python
@staticmethod
def NEW_INDICATOR(data):
    df = data.copy()
    # 计算逻辑
    return df
```

---

## ⚠️ 注意事项

1. **数据延迟**: 免费 API 有 15 分钟延迟
2. **请求频率**: 避免高频请求 (建议间隔>=1 秒)
3. **网络连接**: 确保能访问数据源
4. **Python 版本**: 建议 3.8+

---

**详细代码注释请查看各模块源文件**
