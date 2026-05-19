import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_load_config_missing_required_key(monkeypatch):
    """缺少必填 key 时应抛出 SystemExit"""
    from github_trending_weekly import load_config  # import first so load_dotenv() runs
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    monkeypatch.delenv('SMTP_HOST', raising=False)
    monkeypatch.delenv('SMTP_USER', raising=False)
    monkeypatch.delenv('SMTP_PASS', raising=False)
    monkeypatch.delenv('NOTIFY_TO', raising=False)

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

    # Monday boundary: script runs on Monday, should return last week
    today = date(2026, 5, 18)  # Monday
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

    repos = fetch_trending('2026-05-11', date_to='2026-05-17', github_token='')
    assert len(repos) == 20
    assert repos[0]['name'] == 'owner/repo'
    assert repos[0]['stars'] == 1000
    assert 'url' in repos[0]


def test_summarize_repos_returns_dict(monkeypatch):
    """summarize_repos 返回 {repo_name: summary_str} dict"""
    from github_trending_weekly import summarize_repos

    fake_repos = [
        {'name': 'owner/alpha', 'description': 'Alpha project', 'topics': ['ai']},
        {'name': 'owner/beta', 'description': 'Beta project', 'topics': []},
    ]

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
