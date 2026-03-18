# 📤 推送到 GitHub 指南

## 方法一：手动创建（推荐）

### 1. 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名：`stock-analysis`
3. 描述：`股票分析系统 - 数据采集、技术分析、报告生成`
4. 设为 **Public** 或 **Private**
5. **不要** 勾选 "Add a README file"
6. 点击 "Create repository"

### 2. 推送代码

在仓库页面复制远程地址，然后运行：

```bash
cd C:\Users\aliasy\.openclaw\workspace\stock_analysis

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 方法二：使用 GitHub CLI

### 安装 gh

```powershell
# Windows (winget)
winget install --id GitHub.cli

# 或者下载安装包
# https://github.com/cli/cli/releases
```

### 创建并推送

```bash
cd C:\Users\aliasy\.openclaw\workspace\stock_analysis

# 登录 GitHub
gh auth login

# 创建仓库并推送
gh repo create stock-analysis --public --source=. --remote=origin --push
```

---

## 方法三：使用 Git Token

### 1. 创建 Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制 token

### 2. 推送代码

```bash
cd C:\Users\aliasy\.openclaw\workspace\stock_analysis

# 添加远程仓库（使用 token）
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/stock-analysis.git

# 推送
git branch -M main
git push -u origin main
```

---

## 推送后

仓库将包含：

```
stock-analysis/
├── scripts/              # 核心脚本
│   ├── main.py          # 主程序
│   ├── stock_collector.py    # 数据采集
│   ├── technical_analysis.py # 技术分析
│   ├── report_generator.py   # 报告生成
│   └── wanmei_simple.py      # 示例：完美世界分析
├── data/                # 数据目录
├── reports/             # 报告目录
├── requirements.txt     # Python 依赖
├── run_analysis.bat     # 快速启动
├── README.md            # 使用说明
└── PROJECT_DOCS.md      # 详细文档
```

---

## 常见问题

### 1. 推送失败：Authentication failed

**解决**: 使用 Personal Access Token 代替密码
- https://github.com/settings/tokens

### 2. 仓库已存在

**解决**: 删除远程仓库或更改本地仓库名

### 3. 权限不足

**解决**: 检查 token 是否有 `repo` 权限

---

**需要我帮你自动创建吗？请提供：**
1. GitHub 用户名
2. Personal Access Token（可选，用于自动创建）
