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
