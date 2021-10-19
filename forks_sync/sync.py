import logging
import logging.handlers
import os
import subprocess
from datetime import datetime
from threading import Thread

from github import Github

from forks_sync import DEFAULT_LOCATION
from forks_sync.logger import Logger

TIMEOUT = 180


LOGGER = logging.getLogger(__name__)


class ForksSync:
    def __init__(
        self,
        token=None,
        location=DEFAULT_LOCATION,
    ):
        # Parameter variables
        self.token = token
        self.location = location

        # Internal variables
        self.github_instance = Github(self.token) if self.token else Github()
        self.authenticated_user = self.github_instance.get_user() if self.token else None

    def run(self):
        """Run the Forks Sync script"""
        self.initialize_project()
        start_time = datetime.now()
        Logger.setup_logging(self.location)

        repos = self.get_forked_repos()
        self.iterate_repos(repos)

        execution_time = f'Execution time: {datetime.now() - start_time}.'
        message = (
            f'Forks Sync complete! Your forks are now up to date with their remote default branch.\n{execution_time}'
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

        return forked_repos

    def iterate_repos(self, repos):
        """Iterate over each forked repo and concurrently start an update process"""
        thread_list = []
        for repo in repos:
            repo_path = os.path.join(self.location, 'forks', repo.name)
            fork_thread = Thread(
                target=self.sync_forks,
                args=(
                    repo,
                    repo_path,
                ),
            )
            thread_list.append(fork_thread)
            fork_thread.start()

        for thread in thread_list:
            thread.join()

    def sync_forks(self, repo, repo_path):
        """Sync forks by cloning forks that aren't local
        and rebasing the forked default branch of the ones that are.
        """
        if not os.path.exists(repo_path):
            self.clone_repo(repo, repo_path)

        self.rebase_repo(repo, repo_path)

    def clone_repo(self, repo, repo_path):
        """Clone projects that don't exist locally."""
        command = (
            f'git clone --depth=1 {repo.ssh_url} {repo_path}'
            f' && cd {repo_path}'
            f' && git remote add upstream {repo.parent.clone_url}',
        )

        try:
            subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                check=True,
                timeout=TIMEOUT,
            )
            data = f'{repo.name} cloned!'
            LOGGER.info(data)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out cloning {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            data = f'{repo.name}\n{error}'
            LOGGER.warning(data)

    def rebase_repo(self, repo, repo_path):
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
            subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                check=True,
                timeout=TIMEOUT,
            )
            data = f'{repo.name} rebased!'
            LOGGER.info(data)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out rebasing {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            data = f'{repo.name}\n{error}'
            LOGGER.warning(data)
