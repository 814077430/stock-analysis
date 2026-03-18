# 🌏 全球市场支持 - 使用指南

**已添加**: 港股、美股数据采集和分析

---

## 📦 安装依赖

```bash
pip install yfinance
```

**注意**: 首次安装可能需要几分钟

---

## 🚀 快速开始

### 1. 测试全球数据

```bash
cd stock_analysis
py scripts/global_collector.py
```

**输出示例**:
```
批量获取行情...
✅ CN 000001: 平安银行 10.5
✅ CN 600519: 贵州茅台 1680.0
✅ HK 00700: 腾讯控股 320.5
✅ US AAPL: 苹果 175.0
✅ US TSLA: 特斯拉 250.0
```

### 2. 分析全球股票

```bash
py scripts/global_analysis.py
```

**分析内容**:
- 实时行情
- 涨跌幅
- K 线数据
- 技术指标
- 综合评分
- 交易信号

---

## 📊 支持的市场

### 🇨🇳 A 股
```python
get_quote('000001', 'CN')  # 平安银行
get_quote('600519', 'CN')  # 贵州茅台
```

### 🇭🇰 港股
```python
get_quote('00700', 'HK')   # 腾讯控股
get_quote('9988', 'HK')    # 阿里巴巴
get_quote('1024', 'HK')    # 快手
```

### 🇺🇸 美股
```python
get_quote('AAPL', 'US')    # 苹果
get_quote('GOOGL', 'US')   # 谷歌
get_quote('TSLA', 'US')    # 特斯拉
get_quote('NVDA', 'US')    # 英伟达
get_quote('MSFT', 'US')    # 微软
```

---

## 📋 代码格式

| 市场 | 代码格式 | 示例 |
|------|----------|------|
| A 股 | 6 位数字 | 000001, 600519 |
| 港股 | 5 位数字 | 00700, 9988 |
| 美股 | 股票代码 | AAPL, TSLA |

---

## 🔧 API 说明

### 数据源

| 市场 | 数据源 | 延迟 |
|------|--------|------|
| A 股 | 腾讯财经 | 实时 |
| 港股 | yfinance (雅虎) | 15 分钟 |
| 美股 | yfinance (雅虎) | 15 分钟 |

### 函数接口

```python
from global_collector import get_quote, get_kline

# 获取行情
quote = get_quote('AAPL', 'US')

# 获取 K 线
kline = get_kline('AAPL', 'US', period='1mo')
```

---

## ⚠️ 注意事项

### 1. 数据延迟
- 免费 API 有 15 分钟延迟
- 不适合高频交易

### 2. 交易时间
- A 股：9:30-15:00 (北京时间)
- 港股：9:30-16:00 (北京时间)
- 美股：21:30-4:00 (北京时间)

### 3. 网络要求
- yfinance 需要访问雅虎财经
- 可能需要代理

---

## 📝 示例：监控组合

```python
# 创建一个全球股票监控组合
watchlist = [
    {'code': '000001', 'market': 'CN', 'name': '平安银行'},
    {'code': '600519', 'market': 'CN', 'name': '贵州茅台'},
    {'code': '00700', 'market': 'HK', 'name': '腾讯控股'},
    {'code': 'AAPL', 'market': 'US', 'name': '苹果'},
    {'code': 'TSLA', 'market': 'US', 'name': '特斯拉'},
]

# 批量获取
from global_collector import get_quotes_batch
quotes = get_quotes_batch(watchlist)
```

---

## 🎯 下一步

1. **安装 yfinance**: `pip install yfinance`
2. **测试数据**: `py scripts/global_collector.py`
3. **运行分析**: `py scripts/global_analysis.py`

---

**已集成到主程序**:
```bash
py scripts/main.py  # 现在也支持港股/美股代码
```
