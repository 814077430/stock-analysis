# 📈 股票分析系统 v1.0

**创建时间**: 2026-03-18  
**状态**: ✅ 基础功能完成

---

## 📁 目录结构

```
stock_analysis/
├── scripts/         # 核心脚本
│   ├── main.py              # 主程序
│   ├── stock_collector.py   # 数据采集
│   ├── technical_analysis.py # 技术分析
│   └── report_generator.py  # 报告生成
├── data/          # 股票数据、历史行情
├── reports/       # 分析报告、日报、周报
├── requirements.txt
├── run_analysis.bat
└── README.md
```

---

## 🎯 功能特性

### ✅ 数据采集
- A 股行情数据抓取（腾讯 API）
- K 线历史数据（日线/周线/月线）
- 实时行情
- 自选股监控
- 数据保存（CSV/JSON）

### ✅ 分析功能
- 技术指标分析 (MA, MACD, KDJ, RSI, BOLL, ATR)
- 交易信号识别（金叉/死叉/突破）
- 综合评分系统（0-100 分）
- 操作建议生成

### ✅ 报告生成
- 每日复盘报告
- 个股分析报告
- 周报/月报汇总
- Markdown 格式输出

### ✅ 通知功能
- 飞书 Webhook 通知
- 邮件通知（SMTP）
- 配置文件支持

---

## 🚀 快速开始

### 安装依赖

```bash
cd stock_analysis
pip install -r requirements.txt
```

### 运行完整分析

```bash
# 分析默认自选股
py scripts/main.py

# 分析指定股票
py scripts/main.py --watchlist 000001,600000,000002,600519

# 非交互模式（适合定时任务）
py scripts/main.py --no-prompt

# 只采集数据
py scripts/stock_collector.py

# 只技术分析
py scripts/technical_analysis.py

# 只生成报告
py scripts/report_generator.py
```

### 查看结果

```bash
# 查看报告
ls reports/

# 查看数据
ls data/
```

---

## 📊 数据源

| 类型 | 来源 | 状态 |
|------|------|------|
| A 股实时行情 | 腾讯财经 | ✅ |
| A 股 K 线 | 东方财富 | ✅ |
| 港股 | 待扩展 | ⏳ |
| 美股 | 待扩展 | ⏳ |
| 财报数据 | 待扩展 | ⏳ |
| 新闻舆情 | 待扩展 | ⏳ |

---

## 📋 命令行参数

```bash
py scripts/main.py --help

# 参数说明:
--watchlist 000001,600000  # 自选股代码列表
--no-prompt                # 非交互模式
--notify                   # 启用通知
--config config.json       # 配置文件
```

---

## 📝 扩展计划

- [ ] 港股/美股数据支持
- [ ] 财务数据抓取
- [ ] 基本面分析（PE/PB/ROE）
- [ ] 资金流向分析
- [ ] 板块轮动监控
- [ ] 可视化图表
- [ ] Web 界面

---

**GitHub**: https://github.com/814077430/stock-analysis  
**License**: MIT
