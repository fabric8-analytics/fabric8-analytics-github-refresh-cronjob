"""Test github_refresh.py script."""

from src.github_refresh import schedule_gh_refresh, get_epv_list, run
from src import github_refresh as gh
from unittest import mock


def test_schedule_gh_refresh(mocker):
    """Test schedule_gh_refresh function."""
    epv_list = [
        {
            "ecosystem": "maven",
            "name": "io.vertx-vertx-web"
        }
    ]
    count_mock = mocker.patch('src.github_refresh.refresh')
    count_mock.return_value = 1

    res = schedule_gh_refresh(epv_list)
    assert res is True


def test_get_epv_list(mocker):
    """Test get_epv_list function."""
    gh._REGION = "us-east1"
    gh._ACCESS_KEY = "abcd"
    gh._ACCESS_KEY_ID = "avcd"
    gh._PREFIX = "dev"
    gh._BUCKET = "awsbucket"
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
    assert len(res) == 2
    assert res[0]['ecosystem'] == 'npm'


@mock.patch("src.github_refresh.init_celery")
@mock.patch("src.github_refresh.init_selinon")
@mock.patch("src.github_refresh.get_epv_list")
@mock.patch("src.github_refresh.schedule_gh_refresh")
def test_run(m1, m2, m3, m4):
    """Test run function."""
    m1.return_value = ""
    m2.return_value = ""
    m3.return_value = ""
    m4.return_value = ""
    res = run()
    assert res == "success"
