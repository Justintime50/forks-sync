import subprocess
from unittest.mock import mock_open, patch

import pytest
from forks_sync import ForksSync


@patch('forks_sync.sync.GITHUB_TOKEN', '123')
@patch('forks_sync.sync.USER.get_repos')
@patch('forks_sync.sync.USER')
@patch('forks_sync.sync.ForksSync._setup_logging')
@patch('forks_sync.sync.ForksSync._verify_github_token')
@patch('forks_sync.sync.LOGGER')
def test_run(mock_logger, mock_verify_github_token, mock_setup_logging, mock_user, mock_get_repos):
    ForksSync.run()

    mock_logger.info.assert_called_once()
    mock_verify_github_token.assert_called_once()
    mock_setup_logging.assert_called_once()


@patch('forks_sync.sync.GITHUB_TOKEN', None)
@patch('forks_sync.sync.LOGGER')
def test_verify_github_token(mock_logger):
    message = 'GITHUB_TOKEN must be present to run forks-sync.'
    with pytest.raises(ValueError) as error:
        ForksSync._verify_github_token()
    mock_logger.critical.assert_called_with(message)

    assert message == str(error.value)


@patch('forks_sync.sync.LOG_PATH', 'test/mock-dir')
@patch('forks_sync.sync.LOG_FILE', './test/test.log')
@patch('os.makedirs')
@patch('forks_sync.sync.LOGGER')
def test_setup_logger(mock_logger, mock_make_dirs):
    with patch('builtins.open', mock_open()):
        ForksSync._setup_logging()

    mock_make_dirs.assert_called_once()
    mock_logger.setLevel.assert_called()
    mock_logger.addHandler.assert_called()


@patch('forks_sync.sync.USER.get_repos')
@patch('forks_sync.sync.USER')
def test_get_forked_repos(mock_user, mock_get_repos):
    ForksSync.get_forked_repos()

    mock_get_repos.assert_called_once()


@patch('forks_sync.sync.FORKS_SYNC_LOCATION', 'test')
@patch('forks_sync.sync.ForksSync.sync_forks')
def test_iterate_repos_fork_true(mock_sync_forks, mock_repo):
    mock_repos = [mock_repo]
    ForksSync.iterate_repos(mock_repos)

    mock_sync_forks.assert_called_with(mock_repo, 'test/forks/mock-repo')


@patch('forks_sync.sync.ForksSync.rebase_repo')
@patch('forks_sync.sync.ForksSync.clone_repo')
def test_sync_forks(mock_clone_repo, mock_rebase_repo, mock_repo, mock_repo_path):
    ForksSync.sync_forks(mock_repo, mock_repo_path)

    mock_clone_repo.assert_called_with(mock_repo, mock_repo_path)
    mock_rebase_repo.assert_called_with(mock_repo, mock_repo_path)


@patch('subprocess.run')
@patch('forks_sync.sync.LOGGER')
def test_clone_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync.clone_repo(mock_repo, mock_repo_path)

    mock_logger.info.assert_called_once_with(mock_repo.name + ' cloned!')


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))
def test_clone_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    message = 'Forks Sync timed out cloning ' + mock_repo.name + '.'
    ForksSync.clone_repo(mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_with(message)


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))
def test_clone_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    ForksSync.clone_repo(mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_once()


@patch('subprocess.run')
@patch('forks_sync.sync.LOGGER')
def test_rebase_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync.rebase_repo(mock_repo, mock_repo_path)

    mock_logger.info.assert_called_once_with(mock_repo.name + ' rebased!')


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))
def test_rebase_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    message = 'Forks Sync timed out rebasing ' + mock_repo.name + '.'
    ForksSync.rebase_repo(mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_with(message)


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))
def test_rebase_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    ForksSync.rebase_repo(mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_once()
