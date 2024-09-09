INSTALLED_APPS = (
    'tests',
    'drf_spectacular'
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
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework_json_api.renderers.JSONRenderer",
    )

}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
    'PREPROCESSING_HOOKS': [
        "drf_spectacular_jsonapi.hooks.fix_nested_path_parameters"
    ],
    # drf-spectacular >0.26 added this option which is default True. This feature is not needed and in my pov not best practice to add enum choices...
    "ENUM_GENERATE_CHOICE_DESCRIPTION": False,
    "ENUM_NAME_OVERRIDES": {
        "AlbumTypeEnum": ["Album"],
        "SongTypeEnum": ["Song"],
        "UserTypeEnum": ["User"]
    }
}


ROOT_URLCONF = "tests.urls"
