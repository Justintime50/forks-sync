"""Import modules"""
# pylint: disable=W0511
import os
from datetime import datetime
import sys
import subprocess
import time
from threading import Thread
from github import Github


class Forks():
    """Update your origin forks by rebasing the remote master"""
    USER = Github(os.getenv('API_KEY'))
    REPOS = USER.get_user().get_repos()
    LOG_PATH = os.path.join('logs')
    LOG_FILE = os.path.join(LOG_PATH, f'{datetime.now()}.log')

    @classmethod
    def update(cls, repo, repo_path):
        """Clone forks that aren't local and update ones that are"""
        if not os.path.exists(repo_path):
            # Clone projects that don't exist
            try:
                git = subprocess.check_output(
                    f'git clone --depth=10 --branch=master {repo.ssh_url} {repo_path} ' +
                    f'&& cd {repo_path} && git remote add upstream {repo.parent.clone_url}',
                    stdin=None, stderr=None, shell=True, timeout=120)
                data = f'{repo.name}\nRepo cloned!'
                print(data)
                Forks.logs(data)
            except subprocess.TimeoutExpired:
                sys.exit(f'Error: Forks timed out cloning {repo.name}.')
            except subprocess.CalledProcessError as error:
                data = f'{repo.name}\n{error}'
                print(data)
                Forks.logs(data)

        # Update your origin fork against the upstream master
        try:
            git = subprocess.check_output(
                f'cd {repo_path} && git checkout master && git fetch upstream ' +
                '&& git rebase upstream/master && git push origin -f',
                stdin=None, stderr=None, shell=True, timeout=120)
            data = f'{repo.name}\n{git.decode("UTF-8")}'
            print(data)
            Forks.logs(data)
        except subprocess.TimeoutExpired:
            sys.exit(f'Error: Forks timed out updating {repo.name}.')
        except subprocess.CalledProcessError as error:
            data = f'{repo.name}\n{error}'
            print(data)
            Forks.logs(data)

    @classmethod
    def run(cls):
        """Run the Forks script"""
        start_time = datetime.now()
        # Check if API key is present
        if not os.getenv('API_KEY'):
            sys.exit('API key must be present to run Forks.')
        # Iterate over each repo (fork) and concurrently start an update process
        count = 0
        for repo in Forks.REPOS:
            if repo.fork is True and repo.owner.name == Forks.USER.get_user().name:
                repo_path = os.path.join('forks', repo.name)
                Thread(target=Forks.update, args=(repo, repo_path,)).start()
                time.sleep(1)
                count += 1

        # TODO: Fix this as it will print without checking if each child process is finished.
        execution_time = f'Execution time: {datetime.now() - start_time}. Forks iterated: {count}'
        print('Script complete!', execution_time)

    @classmethod
    def logs(cls, data):
        """Write output to a log"""
        if not os.path.exists(Forks.LOG_PATH):
            os.makedirs(Forks.LOG_PATH)
        try:
            with open(Forks.LOG_FILE, 'a') as log:
                log.write(f'\n{data}\n')
        except OSError as os_error:
            sys.exit(os_error)


Forks.run()
