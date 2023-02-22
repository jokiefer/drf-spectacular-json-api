========================
drf-spectecular-json-api
========================

open api 3 schema generator for `drf-json-api <https://github.com/django-json-api/django-rest-framework-json-api>` package based on `drf-spectacular <https://github.com/tfranzel/drf-spectacular>` package.

Installation
------------

Install using ``pip``\ ...

.. code:: bash

    $ pip install drf-spectacular-jsonapi

then add drf-spectacular to installed apps in ``settings.py``

.. code:: python

    INSTALLED_APPS = [
        # ALL YOUR APPS
        'drf_spectacular',
    ]

and finally register our spectacular AutoSchema with DRF.

.. code:: python

    REST_FRAMEWORK = {
        # YOUR SETTINGS
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular_jsonapi.schemas.openapi.JsonApiAutoSchema",
    }

To expose only json:api request bodys add the following spectacular setting.

.. code:: python

    SPECTACULAR_SETTINGS = {
        # YOUR SETTINGS
        "PARSER_WHITELIST": ["rest_framework_json_api.parsers.JSONParser"]
    }


Release management
^^^^^^^^^^^^^^^^^^

Same as the based *drf-spectacular* package, we provide versions below sem version *1.x.x* to signal that every new version may potentially break you.