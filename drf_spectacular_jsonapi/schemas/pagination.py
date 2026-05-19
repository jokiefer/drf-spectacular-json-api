from typing import Any, Dict

from rest_framework_json_api.pagination import JsonApiPageNumberPagination

# JSON:API link values may be a URI string, a link object, or null. OpenAPI 3.0
# full oneOf for link objects is deferred; nullable URI covers the common case.
# See https://jsonapi.org/format/#document-links


def _top_level_link_value(*, example: Any, description_extra: str = "") -> Dict[str, Any]:
    """helper function to generate schema

    Args:
        example (Any): example of a valid value of this schema
        description_extra (str, optional): additional description for the link. Defaults to "".

    Returns:
        Dict[str, Any]: schema for the link value, which may be a URI string, a link object, or null. OpenAPI 3.0
    """
    
    base = (
        "A JSON:API link: URI string, link object, or null. "
        "See https://jsonapi.org/format/#document-links."
    )
    if description_extra:
        base = f"{description_extra} {base}"
    return {
        "type": "string",
        "format": "uri",
        "nullable": True,
        "example": example,
        "description": base.strip(),
    }


class JsonApiPageNumberPagination(JsonApiPageNumberPagination):

    def get_paginated_response_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a JSON:API document schema for a paginated collection response.

        Top-level ``data`` uses the incoming ``schema`` unchanged. Optional
        ``links`` and ``meta`` follow JSON:API document and pagination rules:
        https://jsonapi.org/format/#fetching-pagination
        """
        # Examples mirror JSON:API's use of http://example.com and page[number]/page[size].
        example_base = "http://example.com/articles?page%5Bsize%5D=10"
        return {
            "type": "object",
            "properties": {
                "data": schema,
                "links": {
                    "type": "object",
                    "description": (
                        "Pagination links for the primary data. These keys MUST be used "
                        "for pagination links; each MUST be omitted or `null` when that "
                        "link is unavailable. Values follow JSON:API link rules (URI string, "
                        "link object, or null). "
                        "https://jsonapi.org/format/#fetching-pagination "
                        "https://jsonapi.org/format/#document-links"
                    ),
                    "properties": {
                        "first": _top_level_link_value(
                            example=f"{example_base}&page%5Bnumber%5D=1",
                            description_extra="The first page of data.",
                        ),
                        "last": _top_level_link_value(
                            example=f"{example_base}&page%5Bnumber%5D=9",
                            description_extra="The last page of data.",
                        ),
                        "prev": _top_level_link_value(
                            example=f"{example_base}&page%5Bnumber%5D=1",
                            description_extra="The previous page of data.",
                        ),
                        "next": _top_level_link_value(
                            example=f"{example_base}&page%5Bnumber%5D=3",
                            description_extra="The next page of data.",
                        ),
                    },
                    "additionalProperties": False,
                },
                "meta": {
                    "type": "object",
                    "description": (
                        "Non-standard meta-information. Page-number stacks often nest "
                        "totals under `pagination`. JSON:API does not define these keys. "
                        "Servers MAY add other `meta` members; this schema documents the "
                        "usual djangorestframework-json-api shape only. "
                        "https://jsonapi.org/format/#document-meta"
                    ),
                    "properties": {
                        "pagination": {
                            "type": "object",
                            "description": (
                                "Typical page-number metadata from "
                                "djangorestframework-json-api; not mandated by JSON:API."
                            ),
                            "properties": {
                                "count": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "example": 42,
                                    "description": "Total number of resources across all pages.",
                                },
                                "page": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "example": 2,
                                    "description": "Current page number (1-based).",
                                },
                                "pages": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "example": 5,
                                    "description": "Total number of pages.",
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "required": ["data"],
        }
