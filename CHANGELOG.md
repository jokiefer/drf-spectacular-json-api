# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note that in line with [Django REST framework policy](https://www.django-rest-framework.org/topics/release-notes/),
any parts of the framework not mentioned in the documentation should generally be considered private API, and may be subject to change.


## [0.1.0] - 2023-02-23

### Added

- initial drf_spectacular_jsonapi app which is based on the drf_spectacular project and patches the basic json:api specific stuff. Basicly the component schemas are representing valid json:api resource objects and the basic query parameters are transported to the schema.
- added general project files such as LICENCE, CHANGELOG, README.
- added python specific project files such as setup.py, requirements and django based test suite.
