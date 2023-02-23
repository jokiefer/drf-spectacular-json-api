from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class JsonApiPageNumberPagination(JsonApiPageNumberPagination):

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                # TODO: add json:api link objects for pagination
                # 'count': {
                #     'type': 'integer',
                #     'example': 123,
                # },
                # 'next': {
                #     'type': 'string',
                #     'nullable': True,
                #     'format': 'uri',
                #     'example': 'http://api.example.org/accounts/?{page_query_param}=4'.format(
                #         page_query_param=self.page_query_param)
                # },
                # 'previous': {
                #     'type': 'string',
                #     'nullable': True,
                #     'format': 'uri',
                #     'example': 'http://api.example.org/accounts/?{page_query_param}=2'.format(
                #         page_query_param=self.page_query_param)
                # },
                'data': {
                    "type": "array",
                    "items": schema
                },
            },
            "required": ["data"]
        }
