"""Test github_refresh.py script."""

from github_refresh import run, TASK_NAMES


def test_run(mocker, db_results):
    """Test the script."""
    count_mock = mocker.patch('github_refresh._get_count')
    count_mock.return_value = 1

    outdated_mock = mocker.patch('github_refresh._get_outdated')
    outdated_mock.return_value = db_results

    schedule_refresh_mock = mocker.patch('github_refresh.run_flow_selective')

    run(None)

    schedule_refresh_mock.assert_called_once_with(
        'bayesianPackageFlow',
        TASK_NAMES,
        {'ecosystem': 'maven', 'package': 'net.iharder:base64', 'force': True},
        True,
        False
    )
