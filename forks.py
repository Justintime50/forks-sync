"""Import modules"""
import os
from datetime import datetime
import sys
import subprocess
from github import Github


class Forks():
    """Update your origin forks by rebasing the remote master"""
    USER = Github(os.getenv('API_KEY'))
    REPOS = USER.get_user().get_repos()
    LOG_PATH = os.path.join('logs')
    LOG_FILE = os.path.join(LOG_PATH, f'{datetime.now()}.log')

    @classmethod
    def run(cls):
        """Run the Forks script"""
        # Check if API key is present
        if not os.getenv('API_KEY'):
            sys.exit('API key must be present to run Forks.')
        # Iterate over each repo (fork)
        for repo in Forks.REPOS:
            if repo.fork is True and repo.owner.name == Forks.USER.get_user().name:
                repo_path = os.path.join('forks', repo.name)

                # Clone projects that don't exist
                if not os.path.exists(repo_path):
                    try:
                        clone = subprocess.check_output(
                            f'git clone --depth=50 --branch=master {repo.ssh_url} {repo_path} ' +
                            '&& cd {repo_path} && git remote add upstream {repo.parent.clone_url}',
                            stdin=None, stderr=None, shell=True, timeout=120)
                        data = f'{repo.name}\n{clone.decode("UTF-8")}'
                        print(data)
                        Forks.logs(data)
                    except subprocess.CalledProcessError as error:
                        data = f'{repo.name}\n{error}'
                        print(data)
                        Forks.logs(data)

                # Update your origin fork against the upstream master
                try:
                    update = subprocess.check_output(
                        f'cd {repo_path} && git checkout master && git fetch upstream ' +
                        '&& git rebase upstream/master && git push origin -f',
                        stdin=None, stderr=None, shell=True, timeout=120)
                    data = f'{repo.name}\n{update.decode("UTF-8")}'
                    print(update)
                    Forks.logs(data)
                except subprocess.CalledProcessError as error:
                    data = f'{repo.name}\n{error}'
                    print(data)
                    Forks.logs(data)

        print('Script complete!')

    @classmethod
    def logs(cls, data):
        """Write output to a log"""
        if not os.path.exists(Forks.LOG_PATH):
            os.makedirs(Forks.LOG_PATH)
        try:
            with open(Forks.LOG_FILE, 'a') as log:
                log.write(f'\n{data}\n')
        except OSError as os_error:
            print(os_error)


Forks.run()
