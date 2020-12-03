"""Test github_refresh.py script."""

from src.github_refresh import schedule_gh_refresh, \
    get_epv_list, run, retrieve_dict, retrieve_blob
from src import github_refresh as gh
from unittest import mock


def test_retrieve_blob():
    """Test retrieve_blob function."""
    res = retrieve_blob("abc")
    assert res is None


@mock.patch('requests_futures.sessions.FuturesSession.post')
def test_schedule_gh_refresh(_mock):
    """Test schedule_gh_refresh function."""
    epv_list = {
        'maven': ['io.vertx:vertx-core'],
        'pypi': ['fastlog'],
        'npm': ['@ng-bootstrap/ng-bootstrap'],
        'golang': ['github.com/shenwei356/unikmer']
    }
    res = schedule_gh_refresh(epv_list)
    assert res is True


def test_get_epv_list(mocker):
    """Test get_epv_list function."""
    mock = mocker.patch('src.github_refresh.retrieve_dict')
    mock.return_value = {
        'stacks_summary': {
            'npm': {
                'unique_dependencies_with_frequency': {
                    'abcd 1.2': 1,
                    'xyz 1.1': 2
                }
            }
        }
    }

    res = get_epv_list()
    assert len(res) == 4
    assert len(res['npm']) == 0

    gh._REGION = "us-east1"
    gh._ACCESS_KEY = "abcd"
    gh._ACCESS_KEY_ID = "avcd"
    gh._PREFIX = "dev"
    gh._BUCKET = "awsbucket"

    res = get_epv_list()
    assert len(res) == 4
    assert len(res['npm']) == 2


def test_retrieve_dict(mocker):
    """Test retrieve_dict."""
    mock = mocker.patch('src.github_refresh.retrieve_blob')
    mock.return_value = None
    res = retrieve_dict("abc")
    assert res is None

    mock.return_value = "{\"a\": \"b\"}".encode()
    res = retrieve_dict("abc")
    assert res['a'] == 'b'


@mock.patch("src.github_refresh.get_epv_list")
@mock.patch("src.github_refresh.schedule_gh_refresh")
def test_run(m1, m2):
    """Test run function."""
    m1.return_value = ""
    m2.return_value = ""
    res = run()
    assert res == "success"
