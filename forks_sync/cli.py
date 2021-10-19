import argparse
import os

from forks_sync import ForksSync

DEFAULT_LOCATION = os.path.expanduser('~/github-archive')


class ForksSyncCli:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Keep all your git forks up to date with the remote main branch.')
        parser.add_argument(
            '-t',
            '--token',
            type=str,
            required=True,
            default=None,
            help='Provide your GitHub token to authenticate with the GitHub API.',
        ),
        parser.add_argument(
            '-l',
            '--location',
            type=str,
            required=False,
            default=DEFAULT_LOCATION,
            help='The location where you want your GitHub Archive to be stored.',
        )
        parser.parse_args(namespace=self)

    def run(self):
        forks_sync = ForksSync(
            token=self.token,
            location=self.location,
        )
        forks_sync.run()


def main():
    ForksSyncCli().run()


if __name__ == '__main__':
    main()
