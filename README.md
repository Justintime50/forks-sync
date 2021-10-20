<div align="center">

# Forks Sync

Keep all your git forks up to date with the remote default branch.

[![Build Status](https://github.com/Justintime50/forks-sync/workflows/build/badge.svg)](https://github.com/Justintime50/forks-sync/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/forks-sync/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/forks-sync?branch=main)
[![PyPi](https://img.shields.io/pypi/v/forks-sync)](https://pypi.org/project/forks-sync)
[![Licence](https://img.shields.io/github/license/justintime50/forks)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/forks-sync/showcase.png" alt="Showcase">

</div>

If you manage more than a couple git forks, keeping them up to date with their remote default branch can be a pain. Forks Sync lets you avoid all the fuss by concurrently cloning each of your projects locally, adding the remote upstream, fetching new changes, rebasing your local default branch against the remote default branch, and `force pushing` to your repo's origin default branch - keeping all your forks up to date with the original repo.

By default, Forks Sync will save all your forks to `~/forks-sync` where you can also find logs for this tool.

**NOTE:** Before proceeding, know that this tool will forcefully update the default branch of your fork to match the upstream default branch.

## Install

```bash
# Install tool
pip3 install forks-sync

# Install locally
make install
```

## Usage

```
Usage:
    forks-sync --token 123...

Options:
    -h, --help            show this help message and exit
    -t TOKEN, --token TOKEN
                            Provide your GitHub token to authenticate with the GitHub API.
    -f, --force           Pass this flag to force push changes to forked repos, otherwise the tool will run in "dry mode".
    -th THREADS, --threads THREADS
                            The number of threads to run.
    -to TIMEOUT, --timeout TIMEOUT
                            The number of seconds before a git operation times out.
    -l LOCATION, --location LOCATION
                            The location where you want your forks and logs to be stored.
```

### Automating SSH Passphrase Prompt (Recommended)

To allow the script to run continuosly without requiring your SSH passphrase, you'll need to add your passphrase to the SSH agent. **NOTE:** Your SSH passphrase will be unloaded upon logout.

```bash
# This assumes you've saved your SSH keys to the default location
ssh-add
```

## Development

```bash
# Get a comprehensive list of development tools
make help

# Run the tool locally
venv/bin/python forks_sync/sync.py
```
