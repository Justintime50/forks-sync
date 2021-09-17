<div align="center">

# Forks Sync

Keep all your git forks up to date with the remote main branch.

[![Build Status](https://github.com/Justintime50/forks-sync/workflows/build/badge.svg)](https://github.com/Justintime50/forks-sync/actions)
[![Coverage Status](https://coveralls.io/repos/github/Justintime50/forks-sync/badge.svg?branch=main)](https://coveralls.io/github/Justintime50/forks-sync?branch=main)
[![PyPi](https://img.shields.io/pypi/v/forks-sync)](https://pypi.org/project/forks-sync)
[![Licence](https://img.shields.io/github/license/justintime50/forks)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/forks-sync/showcase.png" alt="Showcase">

</div>

If you manage more than a couple git forks, keeping them up to date with the remote default branch can be a pain. Forks Sync lets you avoid all the fuss by concurrently cloning each of your projects locally, adding the remote upstream, fetching new changes, rebasing your local default branch against the remote default branch, and `force pushing` to your origin repo's default branch - keeping all your forks up to date with the original repo.

By default, Forks Sync will save all your forks to `~/forks-sync` where you can also find logs for this tool.

**Note:** Before proceeding, know that this tool will forcefully update the default branch of your fork to match the upstream default branch.

## Install

```bash
# Install tool
pip3 install forks-sync

# Install locally
make install

# Get Makefile help
make help
```

## Usage

```bash
# Setup your ssh agent to ensure the script runs continually
ssh-add

# Pass your GitHub API key/token here:
GITHUB_TOKEN=123... forks-sync

# Optional params:
# FORKS_SYNC_LOCATION="~/my-folder"
```

## Development

```bash
# Lint the project
make lint

# Run tests
make test

# Run test coverage
make coverage

# Run the tool locally
venv/bin/python forks_sync/sync.py
```
