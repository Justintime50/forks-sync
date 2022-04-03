import logging
import os
import subprocess
from datetime import datetime
from threading import BoundedSemaphore, Thread
from typing import List, Optional

import woodchips
from github import Github, Repository

from forks_sync.constants import (
    DEFAULT_LOCATION,
    DEFAULT_NUM_THREADS,
    DEFAULT_TIMEOUT,
    LOGGER_NAME,
)

logger = logging.getLogger(__name__)


class ForksSync:
    def __init__(
        self,
        token: Optional[str] = None,
        force: bool = False,
        threads: int = DEFAULT_NUM_THREADS,
        timeout: int = DEFAULT_TIMEOUT,
        location: str = DEFAULT_LOCATION,
    ):
        # Parameter variables
        self.token = token
        self.force = force
        self.threads = threads
        self.timeout = timeout
        self.location = location

        # Internal variables
        self.github_instance = Github(self.token) if self.token else Github()
        if self.token:
            self.authenticated_user = self.github_instance.get_user()

    def run(self):
        """Run the Forks Sync script."""
        self._initialize_project()
        start_time = datetime.now()
        logger = woodchips.get(LOGGER_NAME)
        logger.info('Starting up Forks Sync...')

        repos = self.get_forked_repos()
        self.iterate_repos(repos)

        execution_time = f'Execution time: {datetime.now() - start_time}.'
        if self.force:
            message = (
                'Forks Sync complete! Your forks are now up to date with their remote default'
                f' branch.\n{execution_time}'
            )
        else:
            message = (
                'Forks Sync has completed a dry run. Logs display what would have happened but no action was taken. To'
                ' really run Forks Sync, simply pass the --force flag.'
            )
        logger.info(message)

    def _setup_logger(self):
        """Setup a `woodchips` logger for the project."""
        logger = woodchips.Logger(
            name=LOGGER_NAME,
            level='INFO',
        )
        logger.log_to_console()
        logger.log_to_file(location=os.path.join(self.location, 'logs'))

    def _initialize_project(self):
        """Initialize the tool and ensure everything is in order before running any logic."""
        self._setup_logger()

        if not self.token:
            message = '"token" must be present to run forks-sync.'
            logger.critical(message)
            raise ValueError(message)

    def get_forked_repos(self) -> List[Repository.Repository]:
        """Gets all the repos of a user and returns a list of forks."""
        logger = woodchips.get(LOGGER_NAME)

        repos = self.authenticated_user.get_repos()
        forked_repos = [repo for repo in repos if repo.fork and repo.owner.name == self.authenticated_user.name]
        logger.info('Forks retrieved from GitHub!')

        return forked_repos

    def iterate_repos(self, repos: List[Repository.Repository]):
        """Iterate over each forked repo and concurrently start an update process."""
        thread_limiter = BoundedSemaphore(self.threads)
        thread_list = []

        for repo in repos:
            repo_path = os.path.join(self.location, 'forks', repo.name)
            fork_thread = Thread(
                target=self.sync_forks,
                args=(
                    thread_limiter,
                    repo,
                    repo_path,
                ),
            )
            thread_list.append(fork_thread)
            fork_thread.start()

        # Wait for the number of threads in thread_limiter to finish before moving on
        for thread in thread_list:
            thread.join()

    def sync_forks(self, thread_limiter: BoundedSemaphore, repo: Repository.Repository, repo_path: str):
        """Sync forks by cloning forks that aren't local and rebasing the
        forked default branch of the ones that are.
        """
        if not os.path.exists(repo_path):
            self.clone_repo(thread_limiter, repo, repo_path)

        self.rebase_repo(thread_limiter, repo, repo_path)

    def clone_repo(self, thread_limiter: BoundedSemaphore, repo: Repository.Repository, repo_path: str):
        """Clone projects that don't exist locally."""
        logger = woodchips.get(LOGGER_NAME)

        commands = [
            ['git', 'clone', '--depth=1', repo.ssh_url, repo_path],
            ['git', '-C', repo_path, 'remote', 'add', 'upstream', repo.parent.clone_url],
        ]

        try:
            thread_limiter.acquire()
            if self.force:
                for command in commands:
                    subprocess.run(
                        command,
                        stdin=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        timeout=self.timeout,
                    )
            message = f'{repo.name} cloned!'
            logger.info(message)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out cloning {repo.name}.'
            logger.warning(message)
        except subprocess.CalledProcessError as error:
            message = f'{repo.name}\n{error}'
            logger.warning(message)

    def rebase_repo(self, thread_limiter: BoundedSemaphore, repo: Repository.Repository, repo_path: str):
        """Rebase your origin fork against the upstream default branch."""
        logger = woodchips.get(LOGGER_NAME)

        branch = repo.parent.default_branch
        commands = [
            ['git', '-C', repo_path, 'checkout', branch],
            ['git', '-C', repo_path, 'fetch', 'upstream', '--depth=1'],
            ['git', '-C', repo_path, 'rebase', f'upstream/{branch}'],
            ['git', '-C', repo_path, 'push', 'origin', '-f'],
        ]

        try:
            thread_limiter.acquire()
            if self.force:
                for command in commands:
                    subprocess.run(
                        command,
                        stdin=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        timeout=self.timeout,
                    )
            message = f'{repo.name} rebased!'
            logger.info(message)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out rebasing {repo.name}.'
            logger.warning(message)
        except subprocess.CalledProcessError as error:
            message = f'{repo.name}\n{error}'
            logger.warning(message)
