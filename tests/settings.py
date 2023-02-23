INSTALLED_APPS = (
    'tests',
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular_jsonapi.schemas.openapi.JsonApiAutoSchema",
    "DEFAULT_PAGINATION_CLASS": "drf_spectacular_jsonapi.schemas.pagination.JsonApiPageNumberPagination",

    "DEFAULT_PARSER_CLASSES": (
        "rest_framework_json_api.parsers.JSONParser",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_json_api.filters.QueryParameterValidationFilter",
        "rest_framework_json_api.filters.OrderingFilter",
        'rest_framework_json_api.django_filters.DjangoFilterBackend',
        "rest_framework.filters.SearchFilter",
    ),
    "SEARCH_PARAM": "filter[search]",

}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True
}
