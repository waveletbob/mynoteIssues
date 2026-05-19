# GitHub Trending Weekly — Design Spec

Date: 2026-05-19  
Status: Approved

## Goal

Every Monday, fetch the previous week's hottest GitHub open-source projects, generate Chinese summaries via LLM, and deliver an HTML email digest.

## Architecture

```
cron (每周一 9:00)
  └─▶ scripts/github_trending_weekly.py
        ├─ [1] GitHub Search API  →  Top 20 repos (上周 star 增长最快)
        ├─ [2] Gemini Flash API   →  批量中文摘要 (单次调用)
        └─ [3] SMTP               →  HTML 邮件发送
```

## Data Flow

1. **Time range**: previous Monday 00:00 UTC → previous Sunday 23:59 UTC
2. **GitHub Search query**: `pushed:>=YYYY-MM-DD stars:>50 sort:stars` — top 20
3. **Gemini prompt**: batch all 20 repos in one call, return JSON array `[{"name": "...", "summary": "一句话中文摘要"}]`
4. **Email**: HTML table — rank / project / language / new stars / summary / link

## Components

### github_trending_weekly.py

Single-file script, four logical sections:

| Section | Function | Description |
|---------|----------|-------------|
| Config | `load_config()` | Read `.env`, validate required keys |
| Fetch | `fetch_trending(date_from)` | GitHub Search API, paginate to 20 results |
| Summarize | `summarize_repos(repos)` | Single Gemini batch call, returns dict name→summary |
| Notify | `send_email(repos, summaries)` | Render HTML, send via SMTP SSL |

### Configuration (`.env`)

```
GITHUB_TOKEN=        # optional, raises rate limit 60→5000 req/hr
GEMINI_API_KEY=      # required
SMTP_HOST=           # required, e.g. smtp.gmail.com
SMTP_PORT=465        # SSL port
SMTP_USER=           # sender address
SMTP_PASS=           # sender password / app password
NOTIFY_TO=           # recipient address(es), comma-separated
```

### .env.example

Committed to git. Contains all keys with empty values and comments.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| GitHub rate limit (403/429) | Exponential backoff, max 3 retries |
| GitHub returns < 20 results | Use whatever is returned, no error |
| Gemini API failure | Fallback: use repo `description` field directly |
| SMTP failure | Log error, exit with code 1 (cron-detectable) |
| Missing required env var | Exit with code 1 + clear message on startup |

## Email Format

HTML email, responsive table:

```
Subject: [GitHub Trending] 上周最火开源项目 (YYYY-MM-DD ~ YYYY-MM-DD)

| # | 项目 | 语言 | ⭐新增 | 摘要 | 链接 |
|---|------|------|--------|------|------|
| 1 | ...  | ...  | ...    | ...  | ...  |
```

Plain-text fallback included for non-HTML clients.

## Scheduling

### Local cron
```
0 9 * * 1  cd /path/to/mynoteIssues && python scripts/github_trending_weekly.py
```

### GitHub Actions (alternative)
```yaml
on:
  schedule:
    - cron: '0 1 * * 1'  # UTC 01:00 Monday = CST 09:00
```

## File Structure

```
scripts/
  github_trending_weekly.py   # main script
  .env.example                # config template (committed)
.env                          # actual secrets (gitignored)
```

`.gitignore` entry: `.env`

## Dependencies (additions to requirements.txt)

```
google-generativeai>=0.7.0
python-dotenv>=1.0.0
requests>=2.31.0            # likely already present
```

## Out of Scope

- Persistent storage / history tracking
- Web dashboard
- Multiple notification channels
- Per-language filtering
