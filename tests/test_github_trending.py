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
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)
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
    assert cfg['github_token'] == ''  # optional, defaults to empty string


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
    import requests
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
