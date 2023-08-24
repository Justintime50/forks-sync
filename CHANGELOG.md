# CHANGELOG

## v4.1.0 (2023-08-24)

- Swaps the `ssh_url` for the `clone_url` when cloning repos to remove the unnecessary reliance on having an SSH key or agent to use this tool
- Adds `--version` CLI flag

## v4.0.0 (2023-07-01)

- Drops support for Python 3.7

## v3.0.5 (2023-03-30)

- Fixes a bug that would clobber error output, now it will show correctly
- Bumps all dependencies

## v3.0.4 (2022-04-03)

- Corrects the `git fetch` command to a depth of 1 since we are also shallow cloning repos locally. This should greatly speed up the syncing process for larger repositories since we don't require the entire project tree

## v3.0.3 (2021-12-07)

- Adds `mypy` type checking

## v3.0.2 (2021-11-24)

- Use `woodchips` for logging (same behavior as before)
- Added Python type hinting and stronger test assertions

## v3.0.1 (2021-11-02)

- Refactors the git operations behind the tool to no longer spawn a shell process when using the subprocess module. Removed commands to change directories and instead direct all git commands to the correct path at invocation

## v3.0.0 (2021-10-19)

- Refactors the entire app to use CLI arguments instead of environment variables
- Added a `--force` flag to ensure users don't accidentally blow away their default branches unless they explicitly wanted to. Without passing this flag, the tool will run in "dry mode"
- Now restricts the tool to run with 10 threads by default
- Added additional logging

## v2.3.0 (2021-09-20)

- Drops support for Python 3.6
- Swaps `mock` library for builtin `unittest.mock` library
- Formats project with `Black`

## v2.2.0 (2021-04-12)

- Removed the `branch` flag and functionality as it was causing issues and inconsistencies when cloning/rebasing and branches didn't match up. This became especially prevelant when repos started changing from master to main. Now, we will retrieve the default branch from the parent repo (upstream) and rebase against that. This ensures consistency and safety
- Changed clone depth from 10 to 1

## v2.1.0 (2021-02-04)

- Renamed project from `Forks` to `Forks Sync`, usage and command names however were already that and did not change. This brings the documentation and GitHub references inline with the published package
- Fixed a bug that would attempt to rebase all your org repos unintentionally, now there are checks to ensure the repo belongs to the same person whose GitHub token is used
- Removed references of `master` branch and replaced with `main`
- Added a flag where you can specify the name of your branches (closes #3)
- Switched from Travis CI to GitHub Actions

## v2.0.0 (2020-09-24)

- Added unit tests and test coverage
- Added a Makefile
- Added a CHANGELOG
- Automated releasing via Travis to PyPi
- Updated documentation
- Changed command line invocation from `forks` to `forks-sync`
- Refactored the entire codebase to use smaller units
- Bug fixes
- Added logging, log file rollovers

## v1.0.0 (2020)

- Initial release
