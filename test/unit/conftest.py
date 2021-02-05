import mock
import pytest


@pytest.fixture(scope='module')
def mock_repo():
    mock_repo = mock.Mock()
    mock_repo.name = 'mock-repo'
    mock_repo.fork = True
    return mock_repo


@pytest.fixture(scope='module')
def mock_repo_path():
    return 'test/forks/mock-repo'
