# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note that in line with [Django REST framework policy](https://www.django-rest-framework.org/topics/release-notes/),
any parts of the framework not mentioned in the documentation should generally be considered private API, and may be subject to change.



## [0.4.1] - 2023-12-12


### Fixed

- wrong import path inside apps.py


## [0.4.0] - 2023-12-12


### Fixed

- `ordered` helper function in test suite, which now successfully replace line breaks

### Added

- adds support for drf-spectacular versions above 0.25
- adds support for drf-spectacular versions above 0.25

## [0.3.3] - 2023-11-07

### Fixed

- fixes redundant data framing for response schemas

## [0.3.2] - 2023-08-29

### Fixed

- fixes trailing slashes settings on `fix_nested_path_parameters` hook

## [0.3.1] - 2023-08-29

### Fixed

- fixes `AttributeError 'function' object has no attribute 'cls'` on `fix_nested_path_parameters` hook


## [0.3.0] - 2023-08-29

### Added

- new `fix_nested_path_parameters` to change the path parameter naming for [nested routes](https://chibisov.github.io/drf-extensions/docs/#nested-routes). This hook changes the path parameter name to match `{ResourceType}Id` pattern instead of `parent_lookup_{django_related_name}`.


## [0.2.0] - 2023-08-17

### Added

- add missing `readOnly` attribute to relationships


## [0.1.4] - 2023-08-16

### Fixed

- add missing required definitions of relationships


## [0.1.3] - 2023-07-19

### Fixed

- possible `KeyError` in `_get_response_for_code` function if content is not present in the returned dict of parent class.


## [0.1.2] - 2023-03-22

### Fixed

- title and description translation for all relevant fields

### Changed

- uses drf-spectacular schema information for title and description instead of calculating it by self

## [0.1.1] - 2023-03-02

### Fixed

- removes id from the sparse fieldset query parameters.
- lookup of id field is solved by analyzing the model and then getting the serializer field_name of the detected pk name to resolve the id schema. If no primary key could be detectet, the arbitrary-type is used as schema for the id field.

## [0.1.0] - 2023-02-23

### Added

- initial drf_spectacular_jsonapi app which is based on the drf_spectacular project and patches the basic json:api specific stuff. Basicly the component schemas are representing valid json:api resource objects and the basic query parameters are transported to the schema.
- added general project files such as LICENCE, CHANGELOG, README.
- added python specific project files such as setup.py, requirements and django based test suite.
