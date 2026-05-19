# GitHub Trending Weekly — 使用说明

每周一自动推送上周 GitHub star 增长 Top 20 项目摘要邮件。

## 快速开始

1. 复制配置模板并填写密钥：
   ```bash
   cp scripts/.env.example .env
   # 编辑 .env，填入 GEMINI_API_KEY / SMTP_* / NOTIFY_TO
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 手动测试运行：
   ```bash
   python scripts/github_trending_weekly.py
   ```

## 自动调度

### 方案一：本地 cron

```bash
crontab -e
```

添加（每周一 09:00 运行）：
```
0 9 * * 1 cd /path/to/mynoteIssues && python scripts/github_trending_weekly.py >> /tmp/trending.log 2>&1
```

### 方案二：GitHub Actions

创建 `.github/workflows/trending.yml`：

```yaml
name: GitHub Trending Weekly
on:
  schedule:
    - cron: '0 1 * * 1'   # UTC 01:00 周一 = CST 09:00
  workflow_dispatch:        # 允许手动触发

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/github_trending_weekly.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_PORT: ${{ secrets.SMTP_PORT }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASS: ${{ secrets.SMTP_PASS }}
          NOTIFY_TO: ${{ secrets.NOTIFY_TO }}
```

## 配置项说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `GITHUB_TOKEN` | 否 | PAT，提升限速至 5000 req/hr |
| `GEMINI_API_KEY` | 是 | Google AI Studio 获取 |
| `SMTP_HOST` | 是 | 邮件服务器，如 smtp.gmail.com |
| `SMTP_PORT` | 否 | 默认 465 (SSL) |
| `SMTP_USER` | 是 | 发件人地址 |
| `SMTP_PASS` | 是 | 邮箱密码或应用专用密码 |
| `NOTIFY_TO` | 是 | 收件人，多个用逗号分隔 |
