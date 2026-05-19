# GitHub Trending Weekly Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 每周一自动抓取上周 GitHub star 增长最快的 Top 20 仓库，用 Gemini Flash 生成中文摘要，发送 HTML 邮件。

**Architecture:** 单文件脚本 `scripts/github_trending_weekly.py`，分四段：config 加载 → GitHub Search API 拉取 → Gemini 批量摘要 → SMTP 发送 HTML 邮件。配置全部从 `.env` 读取，不硬编码。

**Tech Stack:** Python 3.8+, `requests`, `google-generativeai`, `python-dotenv`, `smtplib` (stdlib)

---

## File Map

| 文件 | 操作 | 说明 |
|------|------|------|
| `scripts/github_trending_weekly.py` | Create | 主脚本，全部逻辑 |
| `scripts/.env.example` | Create | 配置模板，入 git |
| `.env` | Create (local only) | 实际密钥，不入 git |
| `requirements.txt` | Modify | 追加三个依赖 |
| `.gitignore` | Modify | 确保 `.env` 被忽略 |
| `tests/test_github_trending.py` | Create | 单元测试 |

---

### Task 1: 依赖与配置文件

**Files:**
- Modify: `requirements.txt`
- Modify: `.gitignore`
- Create: `scripts/.env.example`

- [ ] **Step 1: 追加依赖到 requirements.txt**

打开 `requirements.txt`，在文件末尾追加：

```
google-generativeai>=0.7.0
python-dotenv>=1.0.0
requests>=2.31.0
```

- [ ] **Step 2: 确认 .gitignore 包含 .env**

检查项目根目录 `.gitignore`。若无 `.env` 条目，追加：

```
.env
```

- [ ] **Step 3: 创建 scripts/.env.example**

创建 `scripts/.env.example`，内容：

```
# GitHub Personal Access Token (可选，不填则限速 60 req/hr，填了 5000 req/hr)
GITHUB_TOKEN=

# Google Gemini API Key（必填）
# 获取: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=

# SMTP 发件配置（必填）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password

# 收件人，多个用逗号分隔
NOTIFY_TO=you@example.com
```

- [ ] **Step 4: 安装依赖**

```bash
pip install -r requirements.txt
```

Expected: 安装成功，无 error。

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore scripts/.env.example
git commit -m "chore: add dependencies and config template for github trending weekly"
```

---

### Task 2: config 加载 + 测试骨架

**Files:**
- Create: `scripts/github_trending_weekly.py`
- Create: `tests/test_github_trending.py`

- [ ] **Step 1: 写失败测试 — config 加载**

创建 `tests/test_github_trending.py`：

```python
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_load_config_missing_required_key(monkeypatch):
    """缺少必填 key 时应抛出 SystemExit"""
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    monkeypatch.delenv('SMTP_HOST', raising=False)
    monkeypatch.delenv('SMTP_USER', raising=False)
    monkeypatch.delenv('SMTP_PASS', raising=False)
    monkeypatch.delenv('NOTIFY_TO', raising=False)

    from github_trending_weekly import load_config
    with pytest.raises(SystemExit):
        load_config()


def test_load_config_returns_dict(monkeypatch):
    """所有必填 key 存在时返回 dict"""
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    monkeypatch.setenv('SMTP_HOST', 'smtp.test.com')
    monkeypatch.setenv('SMTP_PORT', '465')
    monkeypatch.setenv('SMTP_USER', 'user@test.com')
    monkeypatch.setenv('SMTP_PASS', 'pass')
    monkeypatch.setenv('NOTIFY_TO', 'to@test.com')

    from github_trending_weekly import load_config
    cfg = load_config()
    assert cfg['gemini_api_key'] == 'test-key'
    assert cfg['smtp_host'] == 'smtp.test.com'
    assert cfg['smtp_port'] == 465
    assert cfg['notify_to'] == ['to@test.com']
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_github_trending.py -v
```

Expected: `ImportError` 或 `ModuleNotFoundError`（脚本尚不存在）。

- [ ] **Step 3: 创建脚本骨架 + load_config 实现**

创建 `scripts/github_trending_weekly.py`：

```python
#!/usr/bin/env python3
"""GitHub Trending Weekly — 每周一推送上周最火开源项目摘要邮件"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# 加载脚本同目录下的 .env
_here = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_here, '..', '.env'))


def load_config() -> dict:
    """从环境变量读取配置，缺少必填项则退出。"""
    required = ['GEMINI_API_KEY', 'SMTP_HOST', 'SMTP_USER', 'SMTP_PASS', 'NOTIFY_TO']
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        log.error('缺少必填环境变量: %s', ', '.join(missing))
        sys.exit(1)

    return {
        'github_token': os.getenv('GITHUB_TOKEN', ''),
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'smtp_host': os.getenv('SMTP_HOST'),
        'smtp_port': int(os.getenv('SMTP_PORT', '465')),
        'smtp_user': os.getenv('SMTP_USER'),
        'smtp_pass': os.getenv('SMTP_PASS'),
        'notify_to': [e.strip() for e in os.getenv('NOTIFY_TO', '').split(',') if e.strip()],
    }


if __name__ == '__main__':
    cfg = load_config()
    log.info('Config loaded. SMTP=%s, recipients=%s', cfg['smtp_host'], cfg['notify_to'])
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_github_trending.py -v
```

Expected: 2 tests PASSED。

- [ ] **Step 5: Commit**

```bash
git add scripts/github_trending_weekly.py tests/test_github_trending.py
git commit -m "feat: add config loader with env validation"
```

---

### Task 3: GitHub Search API 拉取 Top 20

**Files:**
- Modify: `scripts/github_trending_weekly.py`
- Modify: `tests/test_github_trending.py`

- [ ] **Step 1: 写失败测试 — fetch_trending**

在 `tests/test_github_trending.py` 末尾追加：

```python
def test_get_date_range():
    """get_date_range 返回上周一到上周日的日期字符串"""
    from github_trending_weekly import get_date_range
    from datetime import date

    # 固定"今天"为 2026-05-19 (周二)
    today = date(2026, 5, 19)
    start, end = get_date_range(today)
    assert start == '2026-05-11'
    assert end == '2026-05-17'


def test_fetch_trending_returns_list(monkeypatch):
    """fetch_trending 返回 list[dict]，每项含 name/description/stars/language/url"""
    import json
    from github_trending_weekly import fetch_trending

    fake_item = {
        'full_name': 'owner/repo',
        'description': 'A cool project',
        'stargazers_count': 1000,
        'language': 'Python',
        'html_url': 'https://github.com/owner/repo',
        'topics': ['ai', 'llm'],
    }
    fake_response = {'items': [fake_item] * 20, 'total_count': 20}

    class FakeResp:
        status_code = 200
        def json(self): return fake_response
        def raise_for_status(self): pass

    monkeypatch.setattr(requests, 'get', lambda *a, **kw: FakeResp())

    repos = fetch_trending('2026-05-11', github_token='')
    assert len(repos) == 20
    assert repos[0]['name'] == 'owner/repo'
    assert repos[0]['stars'] == 1000
    assert 'url' in repos[0]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_github_trending.py::test_get_date_range tests/test_github_trending.py::test_fetch_trending_returns_list -v
```

Expected: FAILED（函数不存在）。

- [ ] **Step 3: 实现 get_date_range 和 fetch_trending**

在 `scripts/github_trending_weekly.py` 的 `load_config` 函数之后追加：

```python
def get_date_range(today=None):
    """返回上周一和上周日的 ISO 日期字符串 (YYYY-MM-DD)。"""
    from datetime import date
    if today is None:
        today = date.today()
    # 上周一 = 今天 - 今天是周几 - 6 天
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')


def fetch_trending(date_from: str, github_token: str = '', top_n: int = 20) -> list[dict]:
    """用 GitHub Search API 获取 date_from 之后 star 最多的仓库，返回标准化列表。"""
    url = 'https://api.github.com/search/repositories'
    headers = {'Accept': 'application/vnd.github+json'}
    if github_token:
        headers['Authorization'] = f'Bearer {github_token}'

    params = {
        'q': f'pushed:>={date_from} stars:>50',
        'sort': 'stars',
        'order': 'desc',
        'per_page': top_n,
        'page': 1,
    }

    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code in (403, 429):
                wait = 2 ** attempt * 5
                log.warning('GitHub rate limit, retry in %ds (attempt %d/3)', wait, attempt + 1)
                import time; time.sleep(wait)
                continue
            resp.raise_for_status()
            items = resp.json().get('items', [])
            return [
                {
                    'name': item['full_name'],
                    'description': item.get('description') or '',
                    'stars': item['stargazers_count'],
                    'language': item.get('language') or 'Unknown',
                    'url': item['html_url'],
                    'topics': item.get('topics', []),
                }
                for item in items[:top_n]
            ]
        except requests.RequestException as e:
            log.error('GitHub API error: %s', e)
            if attempt == 2:
                raise
    return []
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_github_trending.py -v
```

Expected: 4 tests PASSED。

- [ ] **Step 5: Commit**

```bash
git add scripts/github_trending_weekly.py tests/test_github_trending.py
git commit -m "feat: implement github search api fetcher with retry"
```

---

### Task 4: Gemini Flash 批量摘要

**Files:**
- Modify: `scripts/github_trending_weekly.py`
- Modify: `tests/test_github_trending.py`

- [ ] **Step 1: 写失败测试 — summarize_repos**

在 `tests/test_github_trending.py` 末尾追加：

```python
def test_summarize_repos_returns_dict(monkeypatch):
    """summarize_repos 返回 {repo_name: summary_str} dict"""
    from github_trending_weekly import summarize_repos

    fake_repos = [
        {'name': 'owner/alpha', 'description': 'Alpha project', 'topics': ['ai']},
        {'name': 'owner/beta', 'description': 'Beta project', 'topics': []},
    ]

    # Mock Gemini response
    fake_json_text = '[{"name":"owner/alpha","summary":"Alpha 是一个 AI 项目"},{"name":"owner/beta","summary":"Beta 是个工具"}]'

    class FakePart:
        text = fake_json_text

    class FakeContent:
        parts = [FakePart()]

    class FakeCandidate:
        content = FakeContent()

    class FakeResponse:
        candidates = [FakeCandidate()]

    class FakeModel:
        def generate_content(self, prompt): return FakeResponse()

    import google.generativeai as genai
    monkeypatch.setattr(genai, 'configure', lambda **kw: None)
    monkeypatch.setattr(genai, 'GenerativeModel', lambda model: FakeModel())

    result = summarize_repos(fake_repos, gemini_api_key='test-key')
    assert result['owner/alpha'] == 'Alpha 是一个 AI 项目'
    assert result['owner/beta'] == 'Beta 是个工具'


def test_summarize_repos_fallback_on_error(monkeypatch):
    """Gemini 失败时降级返回 description"""
    from github_trending_weekly import summarize_repos

    fake_repos = [{'name': 'owner/repo', 'description': 'Fallback desc', 'topics': []}]

    import google.generativeai as genai
    monkeypatch.setattr(genai, 'configure', lambda **kw: None)
    monkeypatch.setattr(genai, 'GenerativeModel', lambda model: (_ for _ in ()).throw(Exception('API error')))

    result = summarize_repos(fake_repos, gemini_api_key='test-key')
    assert result['owner/repo'] == 'Fallback desc'
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_github_trending.py::test_summarize_repos_returns_dict tests/test_github_trending.py::test_summarize_repos_fallback_on_error -v
```

Expected: FAILED（函数不存在）。

- [ ] **Step 3: 实现 summarize_repos**

在 `scripts/github_trending_weekly.py` 的 `fetch_trending` 函数之后追加：

```python
def summarize_repos(repos: list[dict], gemini_api_key: str) -> dict[str, str]:
    """调用 Gemini Flash 批量生成中文摘要，返回 {repo_name: summary}。
    失败时降级为 repo description。
    """
    import json
    import google.generativeai as genai

    fallback = {r['name']: r['description'] or r['name'] for r in repos}

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        items_text = '\n'.join(
            f'- {r["name"]}: {r["description"]} (topics: {", ".join(r["topics"])})'
            for r in repos
        )
        prompt = f"""以下是 GitHub 上本周最热门的开源项目列表，请为每个项目生成一句简洁的中文摘要（20字以内），
说明这个项目是做什么的。返回严格的 JSON 数组，格式: [{{"name":"owner/repo","summary":"摘要"}}]
不要有任何额外文字，只返回 JSON。

项目列表:
{items_text}"""

        response = model.generate_content(prompt)
        raw = response.candidates[0].content.parts[0].text.strip()
        # 去掉可能的 markdown 代码块
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()

        data = json.loads(raw)
        result = {item['name']: item['summary'] for item in data}
        log.info('Gemini 摘要生成完成，共 %d 项', len(result))
        return result

    except Exception as e:
        log.warning('Gemini 摘要失败，降级使用 description: %s', e)
        return fallback
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_github_trending.py -v
```

Expected: 6 tests PASSED。

- [ ] **Step 5: Commit**

```bash
git add scripts/github_trending_weekly.py tests/test_github_trending.py
git commit -m "feat: add gemini flash batch summarizer with fallback"
```

---

### Task 5: HTML 邮件渲染 + SMTP 发送

**Files:**
- Modify: `scripts/github_trending_weekly.py`
- Modify: `tests/test_github_trending.py`

- [ ] **Step 1: 写失败测试 — render_html**

在 `tests/test_github_trending.py` 末尾追加：

```python
def test_render_html_contains_repo_data():
    """render_html 返回包含仓库名、stars、摘要的 HTML 字符串"""
    from github_trending_weekly import render_html

    repos = [{
        'name': 'owner/awesome',
        'stars': 2500,
        'language': 'Python',
        'url': 'https://github.com/owner/awesome',
        'description': 'An awesome tool',
    }]
    summaries = {'owner/awesome': '这是一个很棒的工具'}
    date_from, date_to = '2026-05-11', '2026-05-17'

    html = render_html(repos, summaries, date_from, date_to)
    assert 'owner/awesome' in html
    assert '2,500' in html or '2500' in html
    assert '这是一个很棒的工具' in html
    assert 'https://github.com/owner/awesome' in html
    assert '2026-05-11' in html


def test_send_email_calls_smtp(monkeypatch):
    """send_email 调用 SMTP 且不抛异常"""
    from github_trending_weekly import send_email
    calls = []

    class FakeSMTP:
        def __init__(self, host, port): calls.append(('init', host, port))
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def login(self, user, pw): calls.append(('login', user))
        def sendmail(self, frm, to, msg): calls.append(('send', frm, to))

    import smtplib
    monkeypatch.setattr(smtplib, 'SMTP_SSL', FakeSMTP)

    cfg = {
        'smtp_host': 'smtp.test.com',
        'smtp_port': 465,
        'smtp_user': 'from@test.com',
        'smtp_pass': 'pass',
        'notify_to': ['to@test.com'],
    }
    send_email('<html>test</html>', 'Subject', cfg)
    assert any(c[0] == 'send' for c in calls)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_github_trending.py::test_render_html_contains_repo_data tests/test_github_trending.py::test_send_email_calls_smtp -v
```

Expected: FAILED（函数不存在）。

- [ ] **Step 3: 实现 render_html 和 send_email**

在 `scripts/github_trending_weekly.py` 的 `summarize_repos` 函数之后追加：

```python
def render_html(repos: list[dict], summaries: dict[str, str], date_from: str, date_to: str) -> str:
    """渲染 HTML 邮件正文。"""
    rows = ''
    for i, repo in enumerate(repos, 1):
        summary = summaries.get(repo['name'], repo['description'] or '')
        stars_fmt = f"{repo['stars']:,}"
        rows += f"""
        <tr>
          <td style="text-align:center;padding:8px 12px;border-bottom:1px solid #eee;">{i}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">
            <a href="{repo['url']}" style="color:#0366d6;text-decoration:none;font-weight:600;">{repo['name']}</a>
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">{repo['language']}</td>
          <td style="text-align:right;padding:8px 12px;border-bottom:1px solid #eee;">⭐ {stars_fmt}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">{summary}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f6f8fa;margin:0;padding:20px;">
  <div style="max-width:900px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">
    <div style="background:#24292e;padding:20px 24px;">
      <h1 style="color:#fff;margin:0;font-size:18px;">🔥 GitHub Trending Weekly</h1>
      <p style="color:#8b949e;margin:4px 0 0;font-size:13px;">{date_from} ~ {date_to} 上周最火开源项目 Top {len(repos)}</p>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <thead>
        <tr style="background:#f6f8fa;">
          <th style="padding:10px 12px;text-align:center;border-bottom:2px solid #e1e4e8;">#</th>
          <th style="padding:10px 12px;text-align:left;border-bottom:2px solid #e1e4e8;">项目</th>
          <th style="padding:10px 12px;text-align:left;border-bottom:2px solid #e1e4e8;">语言</th>
          <th style="padding:10px 12px;text-align:right;border-bottom:2px solid #e1e4e8;">Stars</th>
          <th style="padding:10px 12px;text-align:left;border-bottom:2px solid #e1e4e8;">摘要</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>
    <div style="padding:16px 24px;color:#6a737d;font-size:12px;border-top:1px solid #eee;">
      自动生成 · <a href="https://github.com/waveletbob/mynoteIssues" style="color:#0366d6;">mynoteIssues</a>
    </div>
  </div>
</body>
</html>"""


def send_email(html_body: str, subject: str, cfg: dict) -> None:
    """通过 SMTP SSL 发送 HTML 邮件。失败则抛出异常（由调用方处理）。"""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = cfg['smtp_user']
    msg['To'] = ', '.join(cfg['notify_to'])
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    with smtplib.SMTP_SSL(cfg['smtp_host'], cfg['smtp_port']) as server:
        server.login(cfg['smtp_user'], cfg['smtp_pass'])
        server.sendmail(cfg['smtp_user'], cfg['notify_to'], msg.as_string())
    log.info('邮件发送成功 -> %s', cfg['notify_to'])
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_github_trending.py -v
```

Expected: 8 tests PASSED。

- [ ] **Step 5: Commit**

```bash
git add scripts/github_trending_weekly.py tests/test_github_trending.py
git commit -m "feat: add html email renderer and smtp sender"
```

---

### Task 6: 主入口 + 端到端串联

**Files:**
- Modify: `scripts/github_trending_weekly.py`

- [ ] **Step 1: 替换 `__main__` 块**

将 `scripts/github_trending_weekly.py` 末尾现有的 `if __name__ == '__main__':` 块替换为：

```python
def main():
    cfg = load_config()

    date_from, date_to = get_date_range()
    log.info('抓取 %s ~ %s 的 trending 仓库...', date_from, date_to)

    repos = fetch_trending(date_from, github_token=cfg['github_token'])
    if not repos:
        log.error('未获取到任何仓库，退出')
        sys.exit(1)
    log.info('获取到 %d 个仓库', len(repos))

    summaries = summarize_repos(repos, gemini_api_key=cfg['gemini_api_key'])

    subject = f'[GitHub Trending] 上周最火开源项目 ({date_from} ~ {date_to})'
    html = render_html(repos, summaries, date_from, date_to)

    try:
        send_email(html, subject, cfg)
    except Exception as e:
        log.error('邮件发送失败: %s', e)
        sys.exit(1)

    log.info('完成')


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 运行全量测试确认无回归**

```bash
pytest tests/test_github_trending.py -v
```

Expected: 8 tests PASSED。

- [ ] **Step 3: Commit**

```bash
git add scripts/github_trending_weekly.py
git commit -m "feat: wire up main entry point for github trending weekly"
```

---

### Task 7: Cron 配置说明

**Files:**
- Create: `scripts/README-trending.md`（文档，入 git）

- [ ] **Step 1: 创建使用说明**

创建 `scripts/README-trending.md`：

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add scripts/README-trending.md
git commit -m "docs: add usage guide and cron/github-actions setup instructions"
```

---

## Spec Coverage Check

| Spec 要求 | 对应 Task |
|-----------|-----------|
| 每周一运行 | Task 7 (cron/Actions) |
| 上周时间范围 | Task 3 (get_date_range) |
| GitHub Search API Top 20 | Task 3 (fetch_trending) |
| Gemini Flash 批量摘要 | Task 4 (summarize_repos) |
| Gemini 失败降级 | Task 4 (fallback test) |
| SMTP 邮件发送 | Task 5 (send_email) |
| HTML 邮件格式 | Task 5 (render_html) |
| .env 配置 | Task 1 |
| .env 不入 git | Task 1 (.gitignore) |
| GitHub rate limit retry | Task 3 (fetch_trending) |
