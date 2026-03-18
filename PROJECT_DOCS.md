# 📈 股票分析系统 v1.0 - 项目文档

**创建时间**: 2026-03-18  
**状态**: ✅ 基础功能完成

---

## 📋 项目结构

```
stock_analysis/
├── scripts/              # 核心脚本
│   ├── main.py          # 主程序 (整合采集 + 分析 + 报告)
│   ├── stock_collector.py    # 数据采集模块
│   ├── technical_analysis.py # 技术分析模块
│   └── report_generator.py   # 报告生成模块
├── data/                # 数据目录 (自动创建)
│   ├── stock_list_*.csv      # 股票列表
│   ├── market_snapshot_*.json # 市场快照
│   ├── watchlist_*.csv       # 自选股数据
│   └── stock_*_kline.csv     # K 线数据
├── reports/             # 报告目录 (自动创建)
│   ├── daily_*.md            # 每日复盘报告
│   ├── stock_*_report_*.md   # 个股分析报告
│   └── weekly_*.md           # 周报 (待实现)
├── requirements.txt     # Python 依赖
├── run_analysis.bat     # Windows 快速启动
└── README.md            # 使用说明
```

---

## 🎯 功能模块

### 1. 数据采集 (`stock_collector.py`)

**数据源**:
- ✅ 东方财富 API (实时行情、K 线、股票列表)
- ✅ 新浪财经 API (实时行情、盘口数据)

**功能**:
- ✅ 全市场股票列表采集 (上证/深证/北交所)
- ✅ 实时行情抓取
- ✅ K 线数据 (日线/周线/月线/分钟线)
- ✅ 自选股监控
- ✅ 数据保存 (CSV/JSON)

**API 支持**:
```python
collector = StockDataCollector()

# 全市场数据
market = collector.collect_all_stocks()

# 单只股票详情
detail = collector.collect_stock_detail('000001')

# 自选股
watch = collector.collect_watchlist(['000001', '600000'])

# K 线数据
kline = collector.eastmoney.get_kline('000001', 'day', 100)
```

---

### 2. 技术分析 (`technical_analysis.py`)

**技术指标**:
| 指标 | 说明 | 参数 |
|------|------|------|
| **MA** | 移动平均线 | 5/10/20/60 日 |
| **EMA** | 指数移动平均 | 12/26 日 |
| **MACD** | 平滑异同移动平均 | (12,26,9) |
| **KDJ** | 随机指标 | (9,3,3) |
| **RSI** | 相对强弱指标 | 6/12/24 日 |
| **BOLL** | 布林带 | (20,2) |
| **ATR** | 平均真实波幅 | 14 日 |
| **VOL_MA** | 成交量均线 | 5/10 日 |

**交易信号**:
- 🟢 金叉 (MA/MACD/KDJ)
- 🔴 死叉 (MA/MACD/KDJ)
- 📈 多头排列
- 📉 空头排列
- ⚠️ 超买/超卖
- 🟢 突破信号

**综合评分**:
- 0-100 分制
- 基于技术指标 + 信号汇总
- 操作建议：强烈买入/买入/观望/减仓/卖出

**使用示例**:
```python
analyzer = StockAnalyzer()
result = analyzer.analyze_stock(kline_data)

print(f"评分：{result['score']}/100")
print(f"建议：{result['recommendation']}")
print(f"信号：{result['signals']}")
```

---

### 3. 报告生成 (`report_generator.py`)

**报告类型**:

| 类型 | 频率 | 内容 |
|------|------|------|
| **日报** | 每日 | 市场概览 + 自选股 + 涨幅榜 |
| **个股报告** | 按需 | 详细技术分析 + 操作建议 |
| **周报** | 每周 | 周度回顾 + 下周展望 |

**报告结构**:
```markdown
# 股市日报

## 市场概览
- 股票数量统计
- 涨跌分布

## 涨幅榜/跌幅榜
- Top 10 股票

## 自选股表现
- 价格、涨跌幅、评分、建议

## 个股详细分析
- 技术指标
- 交易信号
- 操作建议
```

**使用示例**:
```python
generator = ReportGenerator()

# 日报
report = generator.generate_daily_report(
    market_data=market,
    watchlist_analysis=analysis
)

# 个股报告
stock_report = generator.generate_stock_report(stock_data)
```

---

## 🚀 使用指南

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行分析 (Windows)
run_analysis.bat

# 或 (Linux/Mac)
python scripts/main.py
```

### 命令行参数

```bash
# 分析默认自选股
py scripts/main.py

# 分析指定股票
py scripts/main.py --watchlist 000001,600000,000002

# 不保存文件
py scripts/main.py --no-save
```

### 独立模块使用

```bash
# 只采集数据
py scripts/stock_collector.py

# 只技术分析
py scripts/technical_analysis.py

# 只生成报告
py scripts/report_generator.py
```

---

## 📊 数据字段说明

### 股票列表字段
| 字段 | 说明 |
|------|------|
| f12 | 股票代码 |
| f14 | 股票名称 |
| f2 | 最新价 |
| f3 | 涨跌幅 |
| f4 | 涨跌额 |
| f5 | 成交量 |
| f6 | 成交额 |

### K 线数据字段
| 字段 | 说明 |
|------|------|
| date | 日期 |
| open | 开盘价 |
| close | 收盘价 |
| high | 最高价 |
| low | 最低价 |
| volume | 成交量 |
| amount | 成交额 |
| turnover | 换手率 |

---

## 🔧 扩展开发

### 添加新数据源

```python
class NewAPISource:
    def __init__(self):
        self.session = requests.Session()
    
    def get_realtime_quotes(self, stock_codes):
        # 实现数据抓取
        pass
```

### 添加新指标

```python
@staticmethod
def NEW_INDICATOR(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    # 计算逻辑
    df['NEW'] = calculation
    return df
```

### 自定义报告模板

```python
class CustomReport(ReportTemplates):
    @staticmethod
    def custom_section(data) -> str:
        return "### 自定义章节\n\n内容..."
```

---

## ⚠️ 注意事项

### 数据准确性
- 实时行情有 15 分钟延迟 (免费 API)
- 复权数据为前复权
- 财报数据需单独获取

### 使用限制
- 东方财富 API 有频率限制
- 建议采集间隔 >= 1 秒
- 避免高频请求

### 风险提示
- 技术指标仅供参考
- 不构成投资建议
- 股市有风险，投资需谨慎

---

## 📝 待办事项

### 数据采集
- [ ] 港股数据 (富途/老虎 API)
- [ ] 美股数据 (Yahoo Finance)
- [ ] 财务数据 (巨潮资讯)
- [ ] 新闻舆情 (财联社)
- [ ] 龙虎榜数据
- [ ] 北向资金流向

### 技术分析
- [ ] 形态识别 (头肩顶、双底等)
- [ ] 波浪理论
- [ ] 缠论分析
- [ ] 自定义指标编辑器

### 报告系统
- [ ] 自动化定时生成
- [ ] 邮件/飞书推送
- [ ] PDF 导出
- [ ] 图表可视化

### 其他功能
- [ ] 选股器 (条件筛选)
- [ ] 回测系统
- [ ] 预警系统
- [ ] Web 界面

---

## 📞 问题反馈

遇到问题？检查以下事项:

1. **依赖安装**: `pip install -r requirements.txt`
2. **网络连接**: 确保能访问东方财富/新浪
3. **Python 版本**: 建议 3.8+
4. **数据目录**: 确保有写入权限

---

**版本**: v1.0  
**最后更新**: 2026-03-18
