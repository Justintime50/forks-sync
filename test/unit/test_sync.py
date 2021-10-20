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
@patch('forks_sync.sync.ForksSync.iterate_repos')
@patch('forks_sync.logger.Logger.setup_logging')
@patch('forks_sync.sync.LOGGER')
def test_run(mock_logger, mock_setup_logging, mock_iterate_repos, mock_get_user):
    ForksSync(
        token='123',
    ).run()

    mock_logger.info.assert_called()


@patch('forks_sync.sync.LOGGER')
def test_initialize_project(mock_logger):
    message = '"token" must be present to run forks-sync.'
    with pytest.raises(ValueError) as error:
        ForksSync(
            token=None,
        ).initialize_project()

    mock_logger.critical.assert_called_with(message)
    assert message == str(error.value)


@patch('forks_sync.sync.ForksSync.sync_forks')
def test_iterate_repos(mock_sync_forks, mock_repo):
    mock_repos = [mock_repo]
    ForksSync(
        token='123',
        location='test',
    ).iterate_repos(mock_repos)

    mock_sync_forks.assert_called()


@patch('forks_sync.sync.ForksSync.rebase_repo')
@patch('forks_sync.sync.ForksSync.clone_repo')
def test_sync_forks(mock_clone_repo, mock_rebase_repo, mock_repo, mock_repo_path):
    ForksSync(
        token='123',
        force=True,
    ).sync_forks(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_clone_repo.assert_called()
    mock_rebase_repo.assert_called()


@patch('subprocess.run')
@patch('forks_sync.sync.LOGGER')
def test_clone_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.info.assert_called_once_with(mock_repo.name + ' cloned!')


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))
def test_clone_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    message = 'Forks Sync timed out cloning ' + mock_repo.name + '.'
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_with(message)


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))
def test_clone_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    ForksSync(
        token='123',
        force=True,
    ).clone_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_once()


@patch('subprocess.run')
@patch('forks_sync.sync.LOGGER')
def test_rebase_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.info.assert_called_once_with(mock_repo.name + ' rebased!')


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))
def test_rebase_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):
    message = 'Forks Sync timed out rebasing ' + mock_repo.name + '.'
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_with(message)


@patch('forks_sync.sync.LOGGER')
@patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))
def test_rebase_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):
    ForksSync(
        token='123',
        force=True,
    ).rebase_repo(mock_thread_limiter(), mock_repo, mock_repo_path)

    mock_logger.warning.assert_called_once()
