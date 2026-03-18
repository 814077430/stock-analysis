# 🌏 全球股票分析系统 v1.0

**GitHub**: https://github.com/814077430/stock-analysis

---

## 📁 项目结构

```
stock_analysis/
├── scripts/
│   ├── main.py              # 主程序
│   ├── data_collector.py    # 数据采集 (A 股/港股/美股)
│   ├── technical_analysis.py # 技术分析
│   └── report_generator.py  # 报告生成
├── data/                    # 数据目录
├── reports/                 # 报告目录
├── requirements.txt
└── README.md
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行分析

```bash
# A 股
py scripts/main.py --market CN

# 港股
py scripts/main.py --market HK

# 美股
py scripts/main.py --market US

# 指定股票
py scripts/main.py --watchlist 000001,600519,AAPL
```

---

## 📊 支持的市场

| 市场 | 代码 | 示例 | 数据源 |
|------|------|------|--------|
| 🇨🇳 A 股 | CN | 000001, 600519 | 腾讯财经 |
| 🇭🇰 港股 | HK | 00700, 9988 | yfinance |
| 🇺🇸 美股 | US | AAPL, TSLA | yfinance |

---

## 🔧 核心功能

### 1. 数据采集 (`data_collector.py`)

**A 股**:
- 实时行情 (腾讯 API)
- K 线数据 (东方财富)

**港股/美股**:
- 实时行情 (yfinance)
- K 线数据 (yfinance)

**统一接口**:
```python
from data_collector import get_quote, get_kline

# 获取行情
quote = get_quote('000001', 'CN')
quote = get_quote('00700', 'HK')
quote = get_quote('AAPL', 'US')

# 获取 K 线
kline = get_kline('000001', 'CN')
```

### 2. 技术分析 (`technical_analysis.py`)

**指标**:
- MA (5/10/20/60)
- MACD
- KDJ
- RSI
- BOLL

**输出**:
- 综合评分 (0-100)
- 操作建议
- 交易信号

### 3. 报告生成 (`report_generator.py`)

**报告类型**:
- 每日复盘
- 个股分析

---

## 📋 命令行参数

```bash
py scripts/main.py --help

--watchlist 000001,AAPL  # 自选股
--market CN/HK/US        # 市场
--no-prompt              # 非交互模式
```

---

## ⚠️ 注意事项

### 1. yfinance 限流
- 每只股票间隔 2-3 秒
- 避免短时间大量请求
- 触发限流后等待 15 分钟

### 2. 数据延迟
- A 股：实时
- 港股/美股：15 分钟延迟

### 3. 网络要求
- yfinance 需访问雅虎财经
- 可能需要代理

---

## 📝 示例输出

```
📊 平安银行 (000001 - CN)
============================================================
💰 价格：10.96
📈 涨跌幅：-0.63%
📊 K 线：100 条

📊 综合评分：45/100
💡 操作建议：🟡 观望

🚨 交易信号:
  ⚠️ 触及布林上轨 (可能回调)
```

---

## 🛠️ 扩展

### 添加新市场
```python
# data_collector.py
def get_xx_quote(code):
    # 实现新市场数据源
    pass
```

### 添加新指标
```python
# technical_analysis.py
@staticmethod
def NEW_INDICATOR(data):
    # 计算逻辑
    return df
```

---

## ⚠️ 风险提示

- 技术指标仅供参考
- 不构成投资建议
- 股市有风险，投资需谨慎

---

**License**: MIT
