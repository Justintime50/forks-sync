import argparse
import logging
import logging.handlers
import os
import subprocess
from datetime import datetime
from threading import Thread

from github import Github

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
USER = Github(GITHUB_TOKEN).get_user()
FORKS_SYNC_LOCATION = os.path.expanduser(
    os.getenv('FORKS_SYNC_LOCATION', '~/forks-sync')
)
LOG_PATH = os.path.join(FORKS_SYNC_LOCATION, 'logs')
LOG_FILE = os.path.join(LOG_PATH, 'forks.log')
LOGGER = logging.getLogger(__name__)
TIMEOUT = 180


class Cli():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Keep all your git forks up to date with the remote main branch.'
        )
        parser.add_argument(
            '-b',
            '--branch',
            required=False,
            default='main',
            type=str,
            help='The branch Forks Sync will rebase against the remote repo.'
        )
        parser.parse_args(namespace=self)

    def run(self):
        ForksSync.run(
            branch=self.branch,
        )


class ForksSync():
    @staticmethod
    def run(branch='main'):
        """Run the Forks Sync script
        """
        start_time = datetime.now()

        ForksSync._setup_logging()
        ForksSync._verify_github_token()
        repos = ForksSync.get_forked_repos()
        ForksSync.iterate_repos(repos, branch)

        execution_time = f'Execution time: {datetime.now() - start_time}.'
        message = f'Forks Sync complete! Your forks are now up to date with their remote {branch} branch.\n{execution_time}'  # noqa
        LOGGER.info(message)

    @staticmethod
    def _verify_github_token():
        """Verify that a GitHub Token is present
        """
        if not GITHUB_TOKEN:
            message = 'GITHUB_TOKEN must be present to run forks-sync.'
            LOGGER.critical(message)
            raise ValueError(message)

    @staticmethod
    def _setup_logging():
        """Setup project logging (to console and log file)
        """
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        LOGGER.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=100000,
            backupCount=5
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        LOGGER.addHandler(logging.StreamHandler())
        LOGGER.addHandler(handler)

    @staticmethod
    def get_forked_repos():
        """Gets all the repos of a user and returns a list of forks
        """
        repos = USER.get_repos()
        forked_repos = [repo for repo in repos if repo.fork and repo.owner.name == USER.name]

        return forked_repos

    @staticmethod
    def iterate_repos(repos, branch='main'):
        """Iterate over each forked repo and concurrently start an update process
        """
        thread_list = []
        for repo in repos:
            repo_path = os.path.join(
                FORKS_SYNC_LOCATION, 'forks', repo.name
            )
            fork_thread = Thread(
                target=ForksSync.sync_forks,
                args=(repo, repo_path, branch,)
            )
            thread_list.append(fork_thread)
            fork_thread.start()

        for thread in thread_list:
            thread.join()

    @staticmethod
    def sync_forks(repo, repo_path, branch='main'):
        """Sync forks by cloning forks that aren't local
        and rebasing the forked master of the ones that are.
        """
        if not os.path.exists(repo_path):
            ForksSync.clone_repo(repo, repo_path)

        ForksSync.rebase_repo(repo, repo_path, branch)

    @staticmethod
    def clone_repo(repo, repo_path):
        """Clone projects that don't exist
        """
        try:
            subprocess.run(
                (
                    f'git clone --depth=10 {repo.ssh_url} {repo_path}'
                    f' && cd {repo_path}'
                    f' && git remote add upstream {repo.parent.clone_url}'
                ),
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                check=True,
                timeout=TIMEOUT
            )
            data = f'{repo.name} cloned!'
            LOGGER.info(data)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out cloning {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            data = f'{repo.name}\n{error}'
            LOGGER.warning(data)

    @staticmethod
    def rebase_repo(repo, repo_path, branch='main'):
        """Rebase your origin fork against the upstream "main" branch
        """
        try:
            subprocess.run(
                (
                    f'cd {repo_path}'
                    f' && git checkout {branch}'
                    f' && git fetch upstream'
                    f' && git rebase upstream/{branch}'
                    f' && git push origin -f'
                ),
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
                check=True,
                timeout=TIMEOUT
            )
            data = f'{repo.name} rebased!'
            LOGGER.info(data)
        except subprocess.TimeoutExpired:
            message = f'Forks Sync timed out rebasing {repo.name}.'
            LOGGER.warning(message)
        except subprocess.CalledProcessError as error:
            data = f'{repo.name}\n{error}'
            LOGGER.warning(data)


def main():
    Cli().run()


if __name__ == '__main__':
    main()
