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
    'drf_spectacular',
    'drf_spectacular_jsonapi',
    'tests',
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular_jsonapi.schemas.openapi.JsonApiAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework_json_api.pagination.JsonApiPageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",
}
