import mock
import pytest
import subprocess
from forks import Forks


@pytest.fixture(scope='module')
def mock_repo():
    mock_repo = mock.Mock()
    mock_repo.name = 'mock-repo'
    mock_repo.fork = True
    return mock_repo


@pytest.fixture(scope='module')
def mock_repo_path():
    return 'test/forks/mock-repo'


@mock.patch('forks.sync.GITHUB_TOKEN', '123')
@mock.patch('forks.sync.USER.get_repos')
@mock.patch('forks.sync.USER')
@mock.patch('forks.sync.Forks.setup_logging')
@mock.patch('forks.sync.Forks.verify_github_token')
@mock.patch('forks.sync.LOGGER')
def test_run(mock_logger, mock_verify_github_token, mock_setup_logging, mock_user, mock_get_repos):  # noqa
    Forks.run()
    mock_logger.info.assert_called_once()
    mock_verify_github_token.assert_called_once()
    mock_setup_logging.assert_called_once()


@mock.patch('forks.sync.GITHUB_TOKEN', None)
@mock.patch('forks.sync.LOGGER')
def test_verify_github_token(mock_logger):
    message = 'GITHUB_TOKEN must be present to run forks-sync.'
    with pytest.raises(ValueError) as error:
        Forks.verify_github_token()
    mock_logger.critical.assert_called_with(message)
    assert message == str(error.value)


@mock.patch('forks.sync.LOG_PATH', 'test/mock-dir')
@mock.patch('forks.sync.LOG_FILE', './test/test.log')
@mock.patch('os.makedirs')
@mock.patch('forks.sync.LOGGER')
def test_setup_logger(mock_logger, mock_make_dirs):
    with mock.patch('builtins.open', mock.mock_open()):
        Forks.setup_logging()
    mock_make_dirs.assert_called_once()
    mock_logger.setLevel.assert_called()
    mock_logger.addHandler.assert_called()


@mock.patch('forks.sync.USER.get_repos')
@mock.patch('forks.sync.USER')
def test_get_repos(mock_user, mock_get_repos):
    Forks.get_repos()
    mock_get_repos.assert_called_once()


@mock.patch('forks.sync.FORKS_SYNC_LOCATION', 'test')
@mock.patch('forks.sync.Forks.sync_forks')
def test_iterate_repos_fork_true(mock_sync_forks, mock_repo):
    mock_repos = [mock_repo]
    Forks.iterate_repos(mock_repos)
    mock_sync_forks.assert_called_with(mock_repo, 'test/forks/mock-repo')


@mock.patch('forks.sync.Forks.sync_forks')
def test_iterate_repos_fork_false(mock_sync_forks, mock_repo):
    mock_repo.fork = False
    mock_repos = [mock_repo]
    Forks.iterate_repos(mock_repos)
    mock_sync_forks.assert_not_called()


@mock.patch('forks.sync.Forks.rebase_repo')
@mock.patch('forks.sync.Forks.clone_repo')
def test_sync_forks(mock_clone_repo, mock_rebase_repo, mock_repo, mock_repo_path):  # noqa
    Forks.sync_forks(mock_repo, mock_repo_path)
    mock_clone_repo.assert_called_with(mock_repo, mock_repo_path)
    mock_rebase_repo.assert_called_with(mock_repo, mock_repo_path)


@mock.patch('subprocess.run')
@mock.patch('forks.sync.LOGGER')
def test_clone_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    Forks.clone_repo(mock_repo, mock_repo_path)
    mock_logger.info.assert_called_once_with(mock_repo.name + ' cloned!')


@mock.patch('forks.sync.LOGGER')
@mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))  # noqa
def test_clone_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):  # noqa
    message = 'Forks timed out cloning ' + mock_repo.name + '.'
    Forks.clone_repo(mock_repo, mock_repo_path)
    mock_logger.warning.assert_called_with(message)


@mock.patch('forks.sync.LOGGER')
@mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))  # noqa
def test_clone_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):  # noqa
    Forks.clone_repo(mock_repo, mock_repo_path)
    mock_logger.warning.assert_called_once()


@mock.patch('subprocess.run')
@mock.patch('forks.sync.LOGGER')
def test_rebase_repo(mock_logger, mock_subprocess, mock_repo, mock_repo_path):
    # TODO: Mock the subprocess better to ensure it does what is intended
    Forks.rebase_repo(mock_repo, mock_repo_path)
    mock_logger.info.assert_called_once_with(mock_repo.name + ' rebased!')


@ mock.patch('forks.sync.LOGGER')
@ mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=subprocess.run, timeout=0.1))  # noqa
def test_rebase_repo_timeout_exception(mock_exception, mock_logger, mock_repo, mock_repo_path):  # noqa
    message = 'Forks timed out rebasing ' + mock_repo.name + '.'
    Forks.rebase_repo(mock_repo, mock_repo_path)
    mock_logger.warning.assert_called_with(message)


@ mock.patch('forks.sync.LOGGER')
@ mock.patch('subprocess.run', side_effect=subprocess.CalledProcessError(returncode=1, cmd=subprocess.run))  # noqa
def test_rebase_repo_called_process_error(mock_exception, mock_logger, mock_repo, mock_repo_path):  # noqa
    Forks.rebase_repo(mock_repo, mock_repo_path)
    mock_logger.warning.assert_called_once()
