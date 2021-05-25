# Changelog


## [1.1.5] - 2021-05-25
### Added
- This `CHANGELOG.md` file
- A `requirements-dev.txt` file for local development
- GitHub pipeline for **pypi** automatic upload on new release
### Changed
- Added `.idea` to the `.gitignore` file for when working with Jetbrains IDE
### Fixed
- Fixed bug where the content-type query would return no result due to forcing label lowercase



## [1.1.4] - 2021-05-25
### Added
- New `get_translation` to get a translated text using an Item id and a Language instance
### Changed
- Updated the `README.md`



## [1.1.3] - 2019-12-13
### Added
- You can now set a default language for your translations
- Added the `set_default_language` to set a default language
### Changed
- `get_language_from_session` became `get_current_language` and always returns a language instance



## [1.1.2] - 2019-10-16
### Fixed
- Removed the migration files (**Highly debatable**)



## [1.1.1] - 2019-10-16
### Fixed
- Fixed the migration files



## [1.1.0] - 2019-10-16
### Added
- Added new utility functions to get translations into your html context
- Added new model Fields shortcuts for our models, such as `ForeignKeyCascade` and `NotEmptyCharField`
### Changed
- Removed the `templatetag` as I couldn't make it work from within a package
- Updated the `README.md`
- Simplified many functions' docstrings



## [1.0.0] - 2019-10-14
First release of our application. Not stable, but it's there I guess :)
