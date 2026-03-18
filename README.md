# 📈 股票分析系统 v1.0

**创建时间**: 2026-03-18  
**GitHub**: https://github.com/814077430/stock-analysis

---

## 📁 目录结构

```
stock_analysis/
├── scripts/
│   ├── main.py                 # 主程序 (采集 + 分析 + 报告)
│   ├── stock_collector.py      # 数据采集
│   ├── technical_analysis.py   # 技术分析
│   └── report_generator.py     # 报告生成
├── data/                       # 数据目录 (自动创建)
├── reports/                    # 报告目录 (自动创建)
├── requirements.txt
├── run_analysis.bat
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
# Windows 双击运行
run_analysis.bat

# 或命令行
py scripts/main.py

# 指定股票
py scripts/main.py --watchlist 000001,600000,000519

# 非交互模式 (定时任务)
py scripts/main.py --no-prompt
```

### 3. 查看结果

```bash
# 查看报告
ls reports/

# 查看数据
ls data/
```

---

## 📊 功能特性

### ✅ 数据采集
- A 股实时行情 (腾讯 API)
- K 线历史数据 (东方财富)
- 全市场股票列表
- 自选股监控

### ✅ 技术分析
- 均线 (MA5/10/20/60)
- MACD 金叉/死叉
- KDJ 超买/超卖
- RSI 强弱指标
- 布林带突破
- 综合评分 (0-100 分)

### ✅ 报告生成
- 每日复盘报告
- 个股分析报告
- Markdown 格式输出

---

## 📋 命令行参数

```bash
py scripts/main.py --help

--watchlist 000001,600000  # 自选股代码
--no-prompt                # 非交互模式
--notify                   # 启用通知
--config config.json       # 配置文件
```

---

## 📝 示例输出

```
📊 综合评分：72/100
💡 操作建议：🟢 建议买入

📉 技术指标:
  MA5:  19.46
  MA10: 19.95
  MACD: 0.06
  KDJ:  65/60

🚨 交易信号:
  🟢 MACD 金叉
  📈 多头排列
```

---

## 🌏 扩展支持 (可选)

### 港股/美股
编辑 `GLOBAL_DATA_SUPPORT.md` 查看详细说明。

```bash
# 安装 yfinance
pip install yfinance

# 港股：0700.HK (腾讯)
# 美股：AAPL (苹果), TSLA (特斯拉)
```

---

## ⚠️ 风险提示

- 技术指标仅供参考
- 数据有 15 分钟延迟
- 不构成投资建议
- 股市有风险，投资需谨慎

---

## 📄 详细文档

- `PROJECT_DOCS.md` - 完整项目文档

---

**License**: MIT
