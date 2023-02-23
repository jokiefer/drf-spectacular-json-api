#DEBUG_PROPAGATE_EXCEPTIONS = True
# DATABASES = {'default': {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': ':memory:'
# }}
#SITE_ID = 1
#SECRET_KEY = 'not very secret in tests'
# USE_I18N = True
# USE_L10N = True
# LANGUAGES = [
#     ('de-de', 'German'),
#     ('en-us', 'English'),
# ]
# LOCALE_PATHS = [
#     base_dir + '/locale/'
# ]
#STATIC_URL = '/static/'
#ROOT_URLCONF = 'tests.urls'
# MIDDLEWARE = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.middleware.locale.LocaleMiddleware',
# )
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_json_api',
    'drf_spectacular',
    'drf_spectacular_jsonapi',
    'tests',
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular_jsonapi.schemas.openapi.JsonApiAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "drf_spectacular_jsonapi.schemas.pagination.JsonApiPageNumberPagination",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    ),

    "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        'rest_framework_json_api.django_filters.DjangoFilterBackend',
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",
    "TEST_REQUEST_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    ),
}

SPECTACULAR_SETTINGS = {
    # YOUR SETTINGS
    "PARSER_WHITELIST": ["rest_framework_json_api.parsers.JSONParser"],
    # 'DEFAULT_GENERATOR_CLASS': 'drf_spectacular_jsonapi.schemas.generators.JsonApiSchemaGenerator',
}
