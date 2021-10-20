import argparse

from forks_sync import ForksSync
from forks_sync.constants import DEFAULT_LOCATION, DEFAULT_NUM_THREADS, DEFAULT_TIMEOUT


class ForksSyncCli:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Keep all your git forks up to date with the remote default branch.'
        )
        parser.add_argument(
            '-t',
            '--token',
            type=str,
            required=True,
            default=None,
            help='Provide your GitHub token to authenticate with the GitHub API.',
        ),
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            required=False,
            default=False,
            help='Pass this flag to force push changes to forked repos, otherwise the tool will run in "dry mode".',
        ),
        parser.add_argument(
            '-th',
            '--threads',
            type=int,
            required=False,
            default=DEFAULT_NUM_THREADS,
            help='The number of threads to run.',
        ),
        parser.add_argument(
            '-to',
            '--timeout',
            type=int,
            required=False,
            default=DEFAULT_TIMEOUT,
            help='The number of seconds before a git operation times out.',
        ),
        parser.add_argument(
            '-l',
            '--location',
            type=str,
            required=False,
            default=DEFAULT_LOCATION,
            help='The location where you want your forks and logs to be stored.',
        ),
        parser.parse_args(namespace=self)

    def run(self):
        forks_sync = ForksSync(
            token=self.token,
            force=self.force,
            threads=self.threads,
            timeout=self.timeout,
            location=self.location,
        )
        forks_sync.run()


def main():
    ForksSyncCli().run()


if __name__ == '__main__':
    main()
