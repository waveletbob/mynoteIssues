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
