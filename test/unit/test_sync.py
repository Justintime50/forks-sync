import subprocess
from threading import BoundedSemaphore
from unittest.mock import patch

import pytest

from forks_sync import ForksSync
from forks_sync.constants import DEFAULT_NUM_THREADS


def mock_thread_limiter():
    thread_limiter = BoundedSemaphore(DEFAULT_NUM_THREADS)

    return thread_limiter


@patch('forks_sync.sync.Github.get_user')
@patch('forks_sync.sync.ForksSync.get_forked_repos')
@patch('forks_sync.sync.ForksSync.iterate_repos')
@patch('forks_sync.sync.ForksSync._setup_logger')
@patch('logging.Logger.info')
def test_run(mock_info_logger, mock_setup_logger, mock_iterate_repos, mock_get_forked_repos, mock_get_user):
    """Test that running the tool works correctly."""
    ForksSync(
        token='123',
    ).run()

    assert mock_info_logger.call_count == 2


@patch('forks_sync.sync.Github.get_user')
@patch('forks_sync.sync.ForksSync.get_forked_repos')
@patch('forks_sync.sync.ForksSync.iterate_repos')
@patch('forks_sync.sync.ForksSync._setup_logger')
@patch('logging.Logger.info')
def test_run_force_flag(mock_info_logger, mock_setup_logger, mock_iterate_repos, mock_get_forked_repos, mock_get_user):
    """Tests that running the tool with the `force` flag works correctly."""
    ForksSync(
        token='123',
        force=True,
    ).run()

    assert mock_info_logger.call_count == 2


@patch('woodchips.Logger')
def test_setup_logger(mock_logger):
    """Tests setting up a `woodchips` logger works."""
    ForksSync()._setup_logger()

    mock_logger.assert_called_once()


@patch('woodchips.Logger')
@patch('logging.Logger.critical')
def test_initialize_project(mock_critical_logger, mock_logger):
    """Tests that we setup the project correctly.

    Added test that we throw an error if no `token` is passed.
    """
    message = '"token" must be present to run forks-sync.'
    with pytest.raises(ValueError) as error:
        ForksSync(
            token=None,
        )._initialize_project()

    mock_logger.assert_called_once()
    mock_critical_logger.assert_called_with(message)
    assert message == str(error.value)


@patch('forks_sync.sync.Github.get_user')
def test_get_forked_repos(mock_get_user):
    """Tests that we return a list of repos (mocked) here."""
    repos = ForksSync(
        token='123',
    ).get_forked_repos()

    assert type(repos) == list


@patch('forks_sync.sync.ForksSync.sync_forks')
def test_iterate_repos(mock_sync_forks, mock_repo):
    """Tests that we call the `sync_forks` method here."""
    mock_repos = [mock_repo]
    ForksSync(
        token='123',
        location='test',
    ).iterate_repos(mock_repos)

    mock_sync_forks.assert_called()


@patch('forks_sync.sync.ForksSync.rebase_repo')
@patch('forks_sync.sync.ForksSync.clone_repo')
def test_sync_forks(mock_clone_repo, mock_rebase_repo, mock_repo, mock_repo_path):
    """Tests that a repo is cloned because it does not yet exist locally."""
    ForksSync(
        token='123',
        force=True,
    ).sync_forks(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_clone_repo.assert_called()
    mock_rebase_repo.assert_called()


@patch('os.path.exists', return_value=True)
@patch('forks_sync.sync.ForksSync.rebase_repo')
@patch('forks_sync.sync.ForksSync.clone_repo')
def test_sync_forks_path_doesnt_exist(mock_clone_repo, mock_rebase_repo, mock_repo, mock_repo_path):
    """Tests that cloning a repo doesn't happen because the dir already exists."""
    ForksSync(
        token='123',
        force=True,
    ).sync_forks(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_clone_repo.assert_not_called()
    mock_rebase_repo.assert_called()


@patch('subprocess.run')
@patch('logging.Logger.info')
def test_clone_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    """Tests that we clone a repo (dry-run)."""
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_subprocess.assert_not_called()  # Don't call since the `force` flag is missing
    mock_logger.assert_called_once_with(mock_repo.name + ' cloned!')


@patch('subprocess.run')
@patch('logging.Logger.info')
def test_clone_repo_force(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    """Tests that we clone a repo (`force` flag)."""
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_subprocess.call_count == 2
    mock_logger.assert_called_once_with(mock_repo.name + ' cloned!')


@patch('logging.Logger.warning')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='subprocess.run', timeout=0.1))
def test_clone_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    """Tests that we throw errors when the subprocess times out."""
    message = 'Forks Sync timed out cloning ' + mock_repo.name + '.'
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.assert_called_with(message)


@patch('logging.Logger.warning')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd='subprocess.run'))
def test_clone_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    """Tests that we throw an error when the subprocess hits an error."""
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.assert_called_once()


@patch('subprocess.run')
@patch('logging.Logger.info')
def test_rebase_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    """Tests that we rebase a repo (dry-run)."""
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_subprocess.assert_not_called()  # Don't call since the `force` flag is missing
    mock_logger.assert_called_once_with(mock_repo.name + ' rebased!')


@patch('subprocess.run')
@patch('logging.Logger.info')
def test_rebase_repo_force(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    """Tests that we rebase a repo (`force` flag)."""
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_subprocess.call_count == 4
    mock_logger.assert_called_once_with(mock_repo.name + ' rebased!')


@patch('logging.Logger.warning')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='subprocess.run', timeout=0.1))
def test_rebase_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    """Tests that we throw errors when the subprocess times out."""
    message = 'Forks Sync timed out rebasing ' + mock_repo.name + '.'
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.assert_called_with(message)


@patch('logging.Logger.warning')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd='subprocess.run'))
def test_rebase_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    """Tests that we throw an error when the subprocess hits an error."""
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.assert_called_once()
