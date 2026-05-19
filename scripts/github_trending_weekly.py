#!/usr/bin/env python3
"""GitHub Trending Weekly — 每周一推送上周最火开源项目摘要邮件"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone

from html import escape

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


def get_date_range(today=None):
    """返回上周一和上周日的 ISO 日期字符串 (YYYY-MM-DD)。"""
    from datetime import date
    if today is None:
        today = date.today()
    # 上周一 = 今天 - 今天是周几 - 6 天
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    return last_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')


def fetch_trending(date_from: str, date_to: str = '', github_token: str = '', top_n: int = 20) -> list[dict]:
    """用 GitHub Search API 获取 date_from 之后 star 最多的仓库，返回标准化列表。"""
    url = 'https://api.github.com/search/repositories'
    headers = {'Accept': 'application/vnd.github+json'}
    if github_token:
        headers['Authorization'] = f'Bearer {github_token}'

    params = {
        'q': f'pushed:{date_from}..{date_to} stars:>50',
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
                time.sleep(wait)
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
    log.error('GitHub rate limit exceeded after 3 attempts, aborting')
    return []


def summarize_repos(repos: list[dict], gemini_api_key: str) -> dict[str, str]:
    """调用 Gemini Flash 批量生成中文摘要，返回 {repo_name: summary}。
    失败时降级为 repo description。
    """
    import json
    import google.generativeai as genai

    fallback = {r['name']: r['description'] or r['name'] for r in repos}

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

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
            <a href="{escape(repo['url'])}" style="color:#0366d6;text-decoration:none;font-weight:600;">{escape(repo['name'])}</a>
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">{escape(repo['language'])}</td>
          <td style="text-align:right;padding:8px 12px;border-bottom:1px solid #eee;">⭐ {stars_fmt}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">{escape(summary)}</td>
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


def main():
    cfg = load_config()

    date_from, date_to = get_date_range()
    log.info('抓取 %s ~ %s 的 trending 仓库...', date_from, date_to)

    repos = fetch_trending(date_from, date_to=date_to, github_token=cfg['github_token'])
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
