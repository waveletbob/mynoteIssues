#!/usr/bin/env python3
"""GitHub Trending Weekly — 每周一推送上周最火开源项目摘要邮件"""

import os
import sys
import time
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


if __name__ == '__main__':
    cfg = load_config()
    log.info('Config loaded. SMTP=%s, recipients=%s', cfg['smtp_host'], cfg['notify_to'])
