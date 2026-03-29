import csv
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from main import load_users_from_csv, scan_v1_sha1_hulud, scan_v2_sha1_hulud, send_notification


def make_csv(rows):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
    writer = csv.writer(f)
    writer.writerow(['Username'])
    for row in rows:
        writer.writerow([row])
    f.close()
    return f.name


def test_load_users_from_csv_basic():
    path = make_csv(['alice', 'bob'])
    try:
        users = load_users_from_csv(path)
        assert users == ['alice', 'bob']
    finally:
        os.unlink(path)


def test_load_users_from_csv_empty():
    path = make_csv([])
    try:
        users = load_users_from_csv(path)
        assert users == []
    finally:
        os.unlink(path)


@patch('main.Github')
def test_scan_v1_found(mock_github_cls):
    mock_g = MagicMock()
    mock_github_cls.return_value = mock_g
    mock_user = MagicMock()
    mock_g.get_user.return_value = mock_user
    mock_user.get_repo.return_value = MagicMock()  # repo exists

    found, url = scan_v1_sha1_hulud('alice')

    assert found is True
    assert url == 'https://github.com/alice/Shai-Hulud'


@patch('main.Github')
def test_scan_v1_not_found(mock_github_cls):
    from github import GithubException
    mock_g = MagicMock()
    mock_github_cls.return_value = mock_g
    mock_user = MagicMock()
    mock_g.get_user.return_value = mock_user
    mock_user.get_repo.side_effect = GithubException(404, 'Not Found', None)

    found, url = scan_v1_sha1_hulud('alice')

    assert found is False
    assert url is None


@patch('main.Github')
def test_scan_v2_found(mock_github_cls):
    mock_g = MagicMock()
    mock_github_cls.return_value = mock_g
    mock_user = MagicMock()
    mock_g.get_user.return_value = mock_user

    mock_repo = MagicMock()
    mock_repo.description = 'Sha1-Hulud: The Second Coming.'
    mock_repo.html_url = 'https://github.com/alice/some-repo'
    mock_user.get_repos.return_value = [mock_repo]

    found, url = scan_v2_sha1_hulud('alice')

    assert found is True
    assert url == 'https://github.com/alice/some-repo'


@patch('main.Github')
def test_scan_v2_not_found(mock_github_cls):
    mock_g = MagicMock()
    mock_github_cls.return_value = mock_g
    mock_user = MagicMock()
    mock_g.get_user.return_value = mock_user

    mock_repo = MagicMock()
    mock_repo.description = 'Some other description'
    mock_user.get_repos.return_value = [mock_repo]

    found, url = scan_v2_sha1_hulud('alice')

    assert found is False
    assert url is None


@patch('main.Github')
def test_scan_v2_no_description(mock_github_cls):
    mock_g = MagicMock()
    mock_github_cls.return_value = mock_g
    mock_user = MagicMock()
    mock_g.get_user.return_value = mock_user

    mock_repo = MagicMock()
    mock_repo.description = None
    mock_user.get_repos.return_value = [mock_repo]

    found, url = scan_v2_sha1_hulud('alice')

    assert found is False
    assert url is None


@patch('main.requests.post')
def test_send_notification(mock_post, monkeypatch):
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/test')
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    send_notification('hello')

    mock_post.assert_called_once_with('https://hooks.slack.com/test', json={'text': 'hello'})
