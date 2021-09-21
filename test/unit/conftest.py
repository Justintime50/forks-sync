from unittest.mock import Mock

import pytest


@pytest.fixture(scope='module')
def mock_repo():
    mock_repo = Mock()
    mock_repo.name = 'mock-repo'
    mock_repo.fork = True

    return mock_repo


@pytest.fixture(scope='module')
def mock_repo_path():

    return 'test/forks/mock-repo'
