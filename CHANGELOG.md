# CHANGELOG

## v2.1.0 (2021-02-04)

* Renamed project from `Forks` to `Forks Sync`, usage and command names however were already that and did not change. This brings the documentation and GitHub references inline with the published package
* Fixed a bug that would attempt to rebase all your org repos unintentionally, now there are checks to ensure the repo belongs to the same person whose GitHub token is used
* Removed references of `master` branch and replaced with `main`
* Added a flag where you can specify the name of your branches (closes #3)
* Switched from Travis CI to GitHub Actions

## v2.0.0 (2020-09-24)

* Added unit tests and test coverage
* Added a Makefile
* Added a CHANGELOG
* Automated releasing via Travis to PyPi
* Updated documentation
* Changed command line invocation from `forks` to `forks-sync`
* Refactored the entire codebase to use smaller units
* Bug fixes
* Added logging, log file rollovers

## v1.0.0 (2020)

* Initial release
