# daily_stock_analysis — 在 mynoteIssues 仓库内部署（克隆上游运行模式）

在 `waveletbob/mynoteIssues` 仓库内运行 https://github.com/ZhuLinsen/daily_stock_analysis ，
**不需要 fork**：workflow 运行时 clone 上游代码，用本仓库里的 `stocks.txt` 作为自选股配置。

## 文件结构

```
mynoteIssues/
├── .github/workflows/daily-stock-analysis.yml   # 主 workflow（克隆上游 + 装依赖 + 跑分析）
└── daily_stock_analysis_deploy/
    ├── README.md                                 # 本说明
    └── stocks.txt                                # 自选股清单（改这里换代码）
```

## 运行流程

1. 检出本仓库 → 拿到 `daily_stock_analysis_deploy/stocks.txt`
2. `git clone --depth 1` 上游 `ZhuLinsen/daily_stock_analysis` 到 `upstream/`
3. `pip install -r upstream/requirements.txt`
4. 解析 `stocks.txt`（去注释/空行，拼成逗号分隔）→ 写入 `STOCK_LIST` 环境变量
5. `cd upstream && python main.py`，Secrets/Variables 从本仓库注入
6. 上传 `upstream/reports/`、`upstream/logs/` 为 artifact（保留 30 天）

## GitHub 端配置（必须在本仓库 waveletbob/mynoteIssues 配置）

1. **Environment**：Settings → Environments → 新建名为 `STOCK_LIST` 的 environment（可为空）。
   workflow 里 `environment: STOCK_LIST` 要求它存在，否则手动触发会一直 pending。
2. **AI Key（必填一个）**：Settings → Secrets and variables → Actions → Secrets：
   - `GEMINI_API_KEY`（免费额度，推荐，https://aistudio.google.com 申请）
   - 或 `AIHUBMIX_KEY` / `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` / `ANTHROPIC_API_KEY`
3. **邮件推送（复用现有 SMTP Secret，无需新建）**：workflow 已把上游的
   `EMAIL_SENDER/EMAIL_PASSWORD/EMAIL_RECEIVERS` 映射到本仓库已有的
   `SMTP_USER/SMTP_PASS/NOTIFY_TO`。只要 `SMTP_USER` 是上游支持自动识别的主流邮箱
   （qq.com / 163.com / 126.com / gmail.com / outlook.com / hotmail.com / live.com /
   sina.com / sohu.com / aliyun.com / 139.com / foxmail.com）即可直接发信。
   上游按发件域名自动识别 SMTP 主机/端口，**不读** `SMTP_HOST/SMTP_PORT`。
   如需单独覆盖，可另建 `EMAIL_SENDER/EMAIL_PASSWORD/EMAIL_RECEIVERS` Secret（优先级更高）。
4. **其它通知渠道（可选，按需）**：在同页 Secrets 加，例如
   `PUSHPLUS_TOKEN`、`WECHAT_WEBHOOK_URL`、`FEISHU_WEBHOOK_URL`、
   `TELEGRAM_BOT_TOKEN`+`TELEGRAM_CHAT_ID` 等。
   （注意：上游 Server酱 用的是 `SERVERCHAN3_SENDKEY`，与本仓库 trending 用的
   `SERVERCHAN_KEY` 不同名，不能直接复用。）
4. **启用 Actions**：Actions 标签 → 确认 "每日股票分析" 已启用 → 点 Run workflow 手动跑一次验证。
   - 首次跑可在弹窗勾选 "强制运行" 跳过交易日检查。
   - `upstream_ref` 输入可指定上游分支/tag，默认 `main`。
5. **定时**：北京时间 18:00（周一~周五）自动运行。
   注意：GitHub 对 60 天无活动仓库会禁用 schedule，到 Actions 页重新启用即可。

## 换股票代码

只改 `daily_stock_analysis_deploy/stocks.txt`，提交一次，下次运行即生效；
想立即验证就手动 Run workflow。

`stocks.txt` 格式：一行一个代码，`#` 后为注释，空行忽略，例如：

```
600519   # 贵州茅台
300750   # 宁德时代
```

## 注意

- `stocks.txt` 只是股票代码，不敏感；**API Key 绝不能写进文件**，必须走 Secrets。
- 上游若改了 `requirements.txt` / `main.py` 接口，本 workflow 直接跟随 `main` 分支生效；
  想锁定版本，手动触发时在 `upstream_ref` 填具体 tag。
