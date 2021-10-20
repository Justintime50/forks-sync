import logging
import os
import subprocess
from datetime import datetime
from threading import BoundedSemaphore, Thread

from github import Github

from forks_sync.constants import DEFAULT_LOCATION, DEFAULT_NUM_THREADS, DEFAULT_TIMEOUT
from forks_sync.logger import Logger

LOGGER = logging.getLogger(__name__)


class ForksSync:
    def __init__(
        self,
        token=None,
        force=False,
        threads=DEFAULT_NUM_THREADS,
        timeout=DEFAULT_TIMEOUT,
        location=DEFAULT_LOCATION,
    ):
        # Parameter variables
        self.token = token
        self.force = force
        self.threads = threads
        self.timeout = timeout
        self.location = location

        # Internal variables
        self.github_instance = Github(self.token) if self.token else Github()
        self.authenticated_user = self.github_instance.get_user() if self.token else None

    def run(self):
        """Run the Forks Sync script"""
        self.initialize_project()
        start_time = datetime.now()
        Logger.setup_logging(LOGGER, self.location)
        LOGGER.info('Starting up Forks Sync...')

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
        LOGGER.info(message)

    def initialize_project(self):
        """Initialize the tool and ensure everything is in order before running any logic."""
        if not self.token:
            message = '"token" must be present to run forks-sync.'
            LOGGER.critical(message)
            raise ValueError(message)

    def get_forked_repos(self):
        """Gets all the repos of a user and returns a list of forks"""
        repos = self.authenticated_user.get_repos()
        forked_repos = [repo for repo in repos if repo.fork and repo.owner.name == self.authenticated_user.name]
        LOGGER.info('Forks retrieved from GitHub!')

        return forked_repos

    def iterate_repos(self, repos):
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

    def sync_forks(self, thread_limiter, repo, repo_path):
        """Sync forks by cloning forks that aren't local
        and rebasing the forked default branch of the ones that are.
        """
        if not os.path.exists(repo_path):
            self.clone_repo(thread_limiter, repo, repo_path)

        self.rebase_repo(thread_limiter, repo, repo_path)

    def clone_repo(self, thread_limiter, repo, repo_path):
        """Clone projects that don't exist locally."""
        command = (
            f'git clone --depth=1 {repo.ssh_url} {repo_path}'
            f' && cd {repo_path}'
            f' && git remote add upstream {repo.parent.clone_url}',
        )

        try:
            thread_limiter.acquire()
            if self.force:
                subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    check=True,
                    timeout=self.timeout,
                )
            message = f'{repo.name} cloned!'
            LOGGER.info(message)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out cloning {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            message = f'{repo.name}\n{error}'
            LOGGER.warning(message)

    def rebase_repo(self, thread_limiter, repo, repo_path):
        """Rebase your origin fork against the upstream default branch"""
        branch = repo.parent.default_branch
        command = (
            f'cd {repo_path}'
            f' && git checkout {branch}'
            ' && git fetch upstream'
            f' && git rebase upstream/{branch}'
            ' && git push origin -f',
        )

        try:
            thread_limiter.acquire()
            if self.force:
                subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    check=True,
                    timeout=self.timeout,
                )
            message = f'{repo.name} rebased!'
            LOGGER.info(message)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out rebasing {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            message = f'{repo.name}\n{error}'
            LOGGER.warning(message)
