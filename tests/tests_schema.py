import json

import rest_framework_json_api
from django.test.testcases import SimpleTestCase
from django.urls import path
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema
from rest_framework.routers import SimpleRouter

from drf_spectacular_jsonapi.schemas.pagination import \
    JsonApiPageNumberPagination
from tests.serializers import (AlbumWithNestedIncludesSerializer,
                               SongWithCreatorSerializer)
from tests.views import (AlbumFilteredViewset, AlbumModelViewset,
                         AlbumWithNestedIncludesViewset, SongModelViewset)


class SimpleSchemaTestCase(SimpleTestCase):

    def ordered(self, obj):
        # don't know why, but enum values are generated in different order in different runs
        # so we order them before comparing them to get reproduceable tests
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        if isinstance(obj, tuple):
            # nested call
            for item in obj:
                self.ordered(item)
        if isinstance(obj, str):
            obj = obj.replace("\n", "")
        return obj

    def setUp(self) -> None:
        self.maxDiff = None
        generator = SchemaGenerator()
        self.schema = generator.get_schema(request=None, public=True)
        # make sure generated schemas are always valid
        validate_schema(self.schema)

        self.json_api_site_package_version = rest_framework_json_api.VERSION


class TestSchemaOutputForSimpleModelSerializer(SimpleSchemaTestCase):

    def test_component_basic_schema(self):
        calculated = self.ordered(
            self.schema["components"]["schemas"]["Album"])
        expected = self.ordered(
            {
                "type": "object",
                "properties": {
                    "type": {
                        "allOf": [{"$ref": "#/components/schemas/AlbumTypeEnum"},],
                        "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                    },
                    "id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "attributes": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "title": "Nice Title",
                                "description": "The title of the Album",
                                "maxLength": 100,
                            },
                            "genre": {
                                "type": "string",
                                "enum": ["POP", "ROCK"],
                                "title": "Nice Genre",
                                "description": "Wich kind of genre this Album represents"
                            },
                            "year": {
                                "type": "integer",
                                "maximum": 2147483647,
                                "minimum": -2147483648,
                                "title": "Nice Year",
                                "description": "The release year"
                            },
                            "released": {
                                "type": "boolean",
                                "title": "Nice Released",
                                "description": "Is this Album released or not?"
                            }
                        },
                        "required": ["title", "genre", "year", "released"],
                    },
                    "relationships": {
                        "type": "object",
                        "properties": {
                            "songs": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string",
                                                    "format": "uuid",
                                                    "title": "Resource Identifier",
                                                    "description": "The identifier of the related object."
                                                },
                                                "type": {
                                                    "type": "string",
                                                    "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                                    "enum": ["Song"],
                                                    "title": "Resource Type Name"
                                                }
                                            },
                                            "required": ["id", "type"],
                                        },
                                    }
                                },
                                "required": ["data"],
                                "title": "Nice Songs",
                                "description": "The songs which are part of this album.",
                            }
                        }
                    }
                },
                "additionalProperties": False,
                "required": ["id", "type"],
            }
        )
        self.assertEqual(expected, calculated)

        calculated = self.ordered(
            self.schema["components"]["schemas"]["Song"])

        expected = self.ordered(
            {
                "type": "object",
                "required": [
                    "type",
                    "id"
                ],
                "additionalProperties": False,
                "properties": {
                    "type": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/SongTypeEnum"
                            }
                        ],
                        "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."
                    },
                    "id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "attributes": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "maxLength": 100
                            },
                            "length": {
                                "type": "integer",
                                "maximum": 2147483647,
                                "minimum": -2147483648
                            }
                        },
                        "required": [
                            "title",
                            "length"
                        ]
                    },
                    "relationships": {
                        "type": "object",
                        "properties": {
                            "created_by": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "string"
                                            },
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "User"
                                                ],
                                                "title": "Resource Type Name",
                                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."
                                            }
                                        },
                                        "required": [
                                            "id",
                                            "type"
                                        ]
                                    }
                                },
                                "required": [
                                    "data"
                                ],
                                "description": "The identifier of the related object.",
                                "title": "Created By",
                                "readOnly": True
                            },
                            "album": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "id": {
                                                "type": "string",
                                                "format": "uuid"
                                            },
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "Album"
                                                ],
                                                "title": "Resource Type Name",
                                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."
                                            }
                                        },
                                        "required": [
                                            "id",
                                            "type"
                                        ]
                                    }
                                },
                                "required": [
                                    "data"
                                ],
                                "description": "The identifier of the related object.",
                                "title": "Album"
                            }
                        },
                        "required": [
                            "album"
                        ]
                    }
                }
            }
        )
        self.assertEqual(expected, calculated)

    def test_get_response_body(self):
        self.assertEqual(
            self.schema["paths"]["/albums/"]["get"]["responses"]["200"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/PaginatedAlbumList"
        )
        paginated = self.schema["components"]["schemas"]["PaginatedAlbumList"]
        self.assertEqual(
            paginated["properties"]["data"]["items"]["$ref"],
            "#/components/schemas/Album"
        )
        self.assertEqual(paginated["required"], ["data"])
        links_schema = paginated["properties"]["links"]
        self.assertIs(links_schema.get("additionalProperties"), False)
        link_props = links_schema["properties"]
        self.assertEqual(
            set(link_props.keys()),
            {"first", "last", "next", "prev"},
        )
        for key in link_props:
            self.assertEqual(link_props[key]["type"], "string")
            self.assertEqual(link_props[key]["format"], "uri")
            self.assertTrue(link_props[key].get("nullable"))
            self.assertIn("example", link_props[key])
        meta_schema = paginated["properties"]["meta"]
        self.assertIs(meta_schema.get("additionalProperties"), False)
        pagination_meta = meta_schema["properties"]["pagination"]
        self.assertIs(pagination_meta.get("additionalProperties"), False)
        self.assertEqual(
            set(pagination_meta["properties"].keys()),
            {"count", "page", "pages"},
        )
        self.assertEqual(
            pagination_meta["properties"]["count"]["type"], "integer")
        self.assertEqual(
            pagination_meta["properties"]["page"]["type"], "integer")
        self.assertEqual(
            pagination_meta["properties"]["pages"]["type"], "integer")
        for key in ("count", "page", "pages"):
            self.assertIn("example", pagination_meta["properties"][key])

        self.assertEqual(
            self.schema["paths"]["/albums/{id}/"]["get"]["responses"]["200"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/AlbumResponse"
        )
        self.assertEqual(
            self.schema["components"]["schemas"]["AlbumResponse"]["properties"]["data"]["$ref"],
            "#/components/schemas/Album"
        )

    def test_post_response_body(self):
        self.assertEqual(
            self.schema["paths"]["/songs/"]["post"]["responses"]["201"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/SongResponse"
        )
        self.assertEqual(
            self.schema["components"]["schemas"]["SongResponse"]["properties"]["data"]["$ref"],
            "#/components/schemas/Song"
        )

    def test_post_only_response_body(self):
        self.assertEqual(
            self.schema["paths"]["/songs-post-only/"]["post"]["responses"]["201"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/SongPostOnlyResponse"
        )
        self.assertEqual(
            self.schema["components"]["schemas"]["SongPostOnlyResponse"]["properties"]["data"]["$ref"],
            "#/components/schemas/SongPostOnly"
        )
        self.assertIn(
            "attributes", self.schema["components"]["schemas"]["SongPostOnly"]["properties"]
        )

    def test_get_parameters(self):
        """Tests if the queryparameters are valid"""
        calculated = self.ordered(
            self.schema["paths"]["/albums/"]["get"]["parameters"])
        expected = self.ordered([
            {
                'in': 'query',
                'name': 'fields[Album]',
                'schema': {'type': 'array', 'items': {'type': 'string', 'enum': ['songs', 'title', 'genre', 'year', 'released']}},
                'description': 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.',
                'explode': False
            },
            {
                # `include=songs` puts Song resources into the same document, and
                # sparse fieldsets are keyed by resource type, so the included
                # resource is documented with a parameter of its own
                'in': 'query',
                'name': 'fields[Song]',
                'schema': {'type': 'array', 'items': {'type': 'string', 'enum': ['album', 'created_by', 'length', 'title']}},
                'description': 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.',
                'explode': False
            },
            {
                'in': 'query',
                'name': 'include',
                'schema': {'type': 'array', 'items': {'type': 'string', 'enum': ['songs']}},
                'description': 'include query parameter to allow the client to customize which related resources should be returned.',
                'explode': False
            },
            {
                'in': 'query',
                'name': 'page[number]',
                'required': False,
                'description': 'A page number within the paginated result set.',
                'schema': {'type': 'integer'}
            },
            {
                'in': 'query',
                'name': 'page[size]',
                'required': False,
                'description': 'Number of results to return per page.',
                'schema': {'type': 'integer'}
            },
            {
                'in': 'query',
                'name': 'sort',
                'required': False,
                'description': 'Which field to use when ordering the results.' if self.json_api_site_package_version == "6.0.0" else '[list of fields to sort by](https://jsonapi.org/format/#fetching-sorting)',
                'schema': {'type': 'array', 'items': {'type': 'string', 'enum': ['id', 'title', '-id', '-title']}},
                'explode': False
            },
            {
                'in': 'query',
                'name': 'filter[search]',
                'required': False,
                'description': 'A search term.',
                'schema': {'type': 'string'}
            },
            {
                'in': 'query',
                'name': 'filter[genre]',
                'description': 'Wich kind of genre this Album represents\n',
                'schema': {'type': 'string', 'title': 'Nice Genre', 'enum': ["POP", "ROCK"]}
            },
            {
                'in': 'query',
                'name': 'filter[title__contains]',
                'schema': {'type': 'string'}
            }
        ])

        self.assertEqual(expected, calculated)

    def test_post_request_body(self):
        """Tests if the request body matches the json:api payload schema"""
        self.assertEqual(
            self.schema["paths"]["/albums/"]["post"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/AlbumRequest"
        )

        calculated = self.schema["components"]["schemas"]["AlbumRequest"]
        expected = {
            "type": "object",
            "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                "enum": ["Album"]
                            },
                            "attributes": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "title": "Nice Title",
                                        "description": "The title of the Album",
                                        "maxLength": 100,
                                        "minLength": 1,
                                    },
                                    "genre": {
                                        "type": "string",
                                        "enum": ["POP", "ROCK"],
                                        "title": "Nice Genre",
                                        "description": "Wich kind of genre this Album represents"
                                    },
                                    "year": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648,
                                        "title": "Nice Year",
                                        "description": "The release year"
                                    },
                                    "released": {
                                        "type": "boolean",
                                        "title": "Nice Released",
                                        "description": "Is this Album released or not?"
                                    }
                                },
                                "required": ["title", "genre", "year", "released"]
                            },
                            "relationships": {
                                "type": "object",
                                "properties": {
                                    "songs": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "string",
                                                            "format": "uuid",
                                                            "title": "Resource Identifier",
                                                            "description": "The identifier of the related object."
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                                            "enum": ["Song"],
                                                            "title": "Resource Type Name"
                                                        }
                                                    },
                                                    "required": ["id", "type"],
                                                },
                                            }
                                        },
                                        "required": ["data"],
                                        "title": "Nice Songs",
                                        "description": "The songs which are part of this album.",
                                    }
                                }
                            }
                        },
                        "required": ["type"],
                        "additionalProperties": False
                    }
            },
            "required": ["data"],
        }

        self.assertJSONEqual(json.dumps(
            calculated, sort_keys=True), json.dumps(expected, sort_keys=True))

        self.assertEqual(
            self.schema["paths"]["/songs/"]["post"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/SongRequest"
        )
        calculated = self.ordered(
            self.schema["components"]["schemas"]["SongRequest"])
        expected = self.ordered(
            {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                "enum": ["Song"]
                            },
                            "attributes": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "maxLength": 100,
                                        "minLength": 1
                                    },
                                    "length": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648
                                    },

                                },
                                "required": ["title", "length"]
                            },
                            "relationships": {
                                "type": "object",
                                "properties": {
                                    "album": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "format": "uuid",
                                                    },
                                                    "type": {
                                                        "type": "string",
                                                        "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                                        "enum": ["Album"],
                                                        "title": "Resource Type Name"
                                                    }
                                                },
                                                "required": ["id", "type"],
                                            }
                                        },
                                        "required": ["data"],
                                        "title": "Album",
                                        "description": "The identifier of the related object.",
                                    },
                                    "created_by": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "minLength": 1,
                                                    },
                                                    "type": {
                                                        "type": "string",
                                                        "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                                        "enum": ["User"],
                                                        "title": "Resource Type Name"
                                                    }
                                                },
                                                "required": ["id", "type"],
                                            }
                                        },
                                        "required": ["data"],
                                        "title": "Created By",
                                        "description": "The identifier of the related object.",
                                        "readOnly": True,
                                    }
                                },
                                "required": ["album"]
                            }
                        },
                        "required": ["type"],
                        "additionalProperties": False
                    }
                },
                "required": ["data"],
            }
        )
        self.assertJSONEqual(json.dumps(
            calculated, sort_keys=True), json.dumps(expected, sort_keys=True))

    def test_patch_request_body(self):
        """Tests if the request body matches the json:api payload schema"""

        self.assertEqual(
            self.schema["paths"]["/albums/{id}/"]["patch"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/PatchedAlbumRequest"
        )

        calculated = self.ordered(
            self.schema["components"]["schemas"]["PatchedAlbumRequest"])
        expected = self.ordered(
            {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                "enum": ["Album"]
                            },
                            "id": {
                                "type": "string",
                                "format": "uuid",
                            },
                            "attributes": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "title": "Nice Title",
                                        "description": "The title of the Album",
                                        "maxLength": 100,
                                        "minLength": 1,
                                    },
                                    "genre": {
                                        "type": "string",
                                        "enum": ["POP", "ROCK"],
                                        "title": "Nice Genre",
                                        "description": "Wich kind of genre this Album represents"
                                    },
                                    "year": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648,
                                        "title": "Nice Year",
                                        "description": "The release year"
                                    },
                                    "released": {
                                        "type": "boolean",
                                        "title": "Nice Released",
                                        "description": "Is this Album released or not?"
                                    }
                                },
                                "required": ["title", "genre", "year", "released"]
                            },
                            "relationships": {
                                "type": "object",
                                "properties": {
                                    "songs": {
                                        "type": "object",
                                        "properties": {
                                            "data": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {
                                                            "type": "string",
                                                            "format": "uuid",
                                                            "title": "Resource Identifier",
                                                            "description": "The identifier of the related object."
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                                            "enum": ["Song"],
                                                            "title": "Resource Type Name"
                                                        }
                                                    },
                                                    "required": ["id", "type"],
                                                },
                                            },
                                        },
                                        "required": ["data"],
                                        "title": "Nice Songs",
                                        "description": "The songs which are part of this album.",
                                    }
                                }
                            }
                        },
                        "required": ["type", "id"],
                        "additionalProperties": False
                    }
                },
                "required": ["data"],
            }
        )
        self.assertEqual(expected, calculated)


class TestJsonApiPageNumberPaginationSchema(SimpleTestCase):
    """Direct tests for paginated JSON:API document envelope schema."""

    def test_get_paginated_response_schema_matches_embedded_document(self):
        paginator = JsonApiPageNumberPagination()
        data_schema = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/Album"},
        }
        envelope = paginator.get_paginated_response_schema(data_schema)
        self.assertIs(envelope["properties"]["data"], data_schema)
        self.assertEqual(envelope["required"], ["data"])

        minimal_openapi = {
            "openapi": "3.0.3",
            "info": {"title": "t", "version": "1"},
            "paths": {
                "/albums/": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/vnd.api+json": {
                                        "schema": envelope,
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Album": {
                        "type": "object",
                        "properties": {"type": {"type": "string"}},
                    }
                }
            },
        }
        validate_schema(minimal_openapi)


class TestSchemaOutputForDifferentIdFieldName(SimpleSchemaTestCase):

    def test_patch_request_body(self):
        """Tests if the request body matches the json:api payload schema"""
        self.assertEqual(

            self.schema["paths"]["/users/{username}/"]["patch"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/PatchedUserRequest"
        )

        calculated = self.ordered(
            self.schema["components"]["schemas"]["PatchedUserRequest"])
        expected = self.ordered(
            {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.",
                                "enum": ["User"]
                            },
                            "id": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 50
                            },
                            "attributes": {
                                "type": "object",
                                "properties": {
                                    "password": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 128
                                    }
                                },
                                "required": ["password"]
                            },
                        },
                        "required": ["type", "id"],
                        "additionalProperties": False
                    }
                },
                "required": ["data"],
            }
        )
        self.assertEqual(expected, calculated)


class TestEmbeddedAttributeSerializerSchema(SimpleSchemaTestCase):
    """Non-resource serializers nested under attributes are plain JSON Schema objects."""

    def test_inline_request_component_not_jsonapi_resource_shape(self):
        emb = self.schema["components"]["schemas"]["EmbeddedDimensionsRequest"]
        self.assertEqual(emb["type"], "object")
        self.assertIn("width", emb["properties"])
        self.assertIn("height", emb["properties"])
        props = emb["properties"]
        self.assertNotIn("attributes", emb)
        self.assertNotIn("relationships", emb)
        # JSON:API resource identification lives under ``properties``; OpenAPI's
        # root ``type`` keyword is only the JSON Schema type tag.
        self.assertNotIn("type", props)

    def test_inline_response_component_not_jsonapi_resource_shape(self):
        emb = self.schema["components"]["schemas"]["EmbeddedDimensions"]
        self.assertEqual(emb["type"], "object")
        self.assertIn("width", emb["properties"])
        self.assertIn("height", emb["properties"])
        self.assertNotIn("type", emb["properties"])

    def test_parent_post_request_dimensions_ref_plain_object(self):
        self.assertEqual(
            self.schema["paths"]["/albums-with-embedded/"]["post"]["requestBody"][
                "content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/AlbumWithEmbeddedRequest",
        )
        dim = self.schema["components"]["schemas"]["AlbumWithEmbeddedRequest"]["properties"][
            "data"]["properties"]["attributes"]["properties"]["dimensions"]
        self.assertIn("$ref", dim)
        self.assertTrue(dim["$ref"].endswith("EmbeddedDimensionsRequest"))


class TestSchemaOutputForNestedResources(SimpleSchemaTestCase):
    def test_nested_path_parameter_fix(self):
        calculated = self.ordered(
            self.schema["paths"]["/albums/{AlbumId}/songs/"]["get"]["parameters"])
        expected = self.ordered(
            [
                [('description', 'A page number within the paginated result set.'), ('in', 'query'),
                 ('name', 'page[number]'), ('required', False), ('schema', [('type', 'integer')])],
                [('description', 'A search term.'), ('in', 'query'), ('name',
                                                                      'filter[search]'), ('required', False), ('schema', [('type', 'string')])],
                [('description', 'Number of results to return per page.'), ('in', 'query'),
                 ('name', 'page[size]'), ('required', False), ('schema', [('type', 'integer')])],
                [('description', 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.'), ('explode', False),
                 ('in', 'query'), ('name', 'fields[Song]'), ('schema', [('items', [('enum', ['album', 'created_by', 'length', 'title']), ('type', 'string')]), ('type', 'array')])],
                [('in', 'path'), ('name', 'AlbumId'), ('required', True), ('schema', [('type', 'string')])]]
        )
        self.assertEqual(expected, calculated)

    def test_nested_path_parameters_songs_as_view(self):
        calculated = self.ordered(
            self.schema["paths"]["/albums/{AlbumId}/songs-as-view/"]["get"]["parameters"])

        expected = self.ordered(
            [
                [('description', 'A page number within the paginated result set.'), ('in', 'query'),
                 ('name', 'page[number]'), ('required', False), ('schema', [('type', 'integer')])],
                [('description', 'A search term.'), ('in', 'query'), ('name',
                                                                      'filter[search]'), ('required', False), ('schema', [('type', 'string')])],
                [('description', 'Number of results to return per page.'), ('in', 'query'),
                 ('name', 'page[size]'), ('required', False), ('schema', [('type', 'integer')])],
                [('description', 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.'), ('explode', False),
                 ('in', 'query'), ('name', 'fields[Song]'), ('schema', [('items', [('enum', ['album', 'created_by', 'length', 'title']), ('type', 'string')]), ('type', 'array')])],
                [('in', 'path'), ('name', 'AlbumId'), ('required', True), ('schema', [('type', 'string')])]]
        )
        self.assertEqual(expected, calculated)


class TestSchemaOutputForRelationshipView(SimpleSchemaTestCase):

    def test_relationshipview_get_operation(self):
        calculated = self.ordered(
            self.schema["paths"]["/albums/{id}/relationships/{related_field}"]["get"]["parameters"])
        expected = self.ordered(
            [
                [
                    ('description', 'A UUID string identifying this album.'),
                    ('in', 'path'),
                    ('name', 'id'),
                    ('required', True),
                    ('schema', [('format', 'uuid'), ('type', 'string')])
                ],
                [
                    ('description', 'Pass in one of the possible relation types to get all related objects.'),
                    ('in', 'path'),
                    ('name', 'related_field'),
                    ('required', True),
                    ('schema', [('enum', ['single']), ('pattern', '^[-/w]+$'), ('type', 'string')])]
            ]
        )
        self.assertEqual(expected, calculated)

        calculated = self.ordered(
            self.schema["paths"]["/albums/{id}/relationships/{related_field}"]["get"]["tags"])
        expected = self.ordered(
            [
                "Song",
                "RelationshipViews"
            ]
        )
        self.assertEqual(expected, calculated)

        calculated = self.ordered(
            self.schema["paths"]["/songs/{id}/relationships/{related_field}"]["get"]["parameters"])
        expected = self.ordered(
            [
                [
                    ('description', 'A UUID string identifying this song.'),
                    ('in', 'path'),
                    ('name', 'id'),
                    ('required', True),
                    ('schema', [('format', 'uuid'), ('type', 'string')])
                ],
                [
                    ('description', 'Pass in one of the possible relation types to get all related objects.'),
                    ('in', 'path'),
                    ('name', 'related_field'),
                    ('required', True),
                    ('schema', [('enum', ['album', 'created_by', 'specialsong']), ('pattern', '^[-/w]+$'), ('type', 'string')])]
            ]
        )
        self.assertEqual(expected, calculated)

        calculated = self.ordered(
            self.schema["paths"]["/songs/{id}/relationships/{related_field}"]["get"]["tags"])
        expected = self.ordered(
            [
                "Album",
                "User",
                "RelationshipViews",
                "SpecialSong"
            ]
        )
        self.assertEqual(expected, calculated)

    def test_relationshipview_get_response(self):
        self.assertEqual(
            self.schema["paths"]["/albums/{id}/relationships/{related_field}"]["get"][
                "responses"]["200"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/AlbumRelationShipsResponse"
        )
        self.assertEqual(
            self.schema["components"]["schemas"]["AlbumRelationShipsResponse"]["properties"]["data"]["$ref"],
            "#/components/schemas/AlbumRelationShips"
        )

        calculated = self.ordered(
            self.schema["components"]["schemas"]["AlbumRelationShips"])
        expected = self.ordered(
            [('oneOf',
              [[('items',
                  [('additionalProperties', False),
                   ('properties',
                    [('id', [('format', 'uuid'), ('readOnly', True), ('type', 'string')]),
                     ('type',
                      [('description',
                        'The '
                        '[type](https://jsonapi.org/format/#document-resource-object-identification) '
                        'member is used to describe resource objects that share common '
                        'attributes and relationships.'),
                       ('enum', ['Song']),
                          ('type', 'string')])]),
                      ('required', ['type']),
                      ('type', 'object')]),
                  ('type', 'array')]])]
        )
        self.assertEqual(expected, calculated)


class TestOasValidityOfFilterParameterTitle(SimpleSchemaTestCase):
    """
    A declared filter's label is documented on the parameter. It must not become a
    "title" member of the Parameter Object, because OAS 3.0 has no such member there
    and spec validators reject the whole document because of it.
    """

    def setUp(self) -> None:
        self.maxDiff = None
        router = SimpleRouter()
        router.register(
            "filtered-albums", AlbumFilteredViewset, basename="filtered-album")
        generator = SchemaGenerator(patterns=router.urls)
        self.schema = generator.get_schema(request=None, public=True)

    def all_parameters(self):
        for url, path_item in self.schema["paths"].items():
            for member, value in path_item.items():
                if member == "parameters":
                    for parameter in value:
                        yield parameter
                elif isinstance(value, dict):
                    for parameter in value.get("parameters", []):
                        yield parameter

    def test_filter_label_is_documented_on_the_parameter_schema(self):
        parameters = self.schema["paths"]["/filtered-albums/"]["get"]["parameters"]
        parameter = [p for p in parameters if p["name"] == "filter[year]"][0]

        self.assertEqual(
            parameter["schema"]["title"], "Wich year this Album represents")
        self.assertNotIn("title", parameter)

    def test_no_parameter_object_carries_a_title(self):
        for parameter in self.all_parameters():
            self.assertNotIn("title", parameter)

    def test_the_document_validates(self):
        validate_schema(self.schema)


class TestSparseFieldsetsOfIncludedResources(SimpleSchemaTestCase):
    """
    A sparse fieldset is keyed by resource type, not by the resource the endpoint
    answers: ``SparseFieldsetsMixin`` reads ``fields[TYPE]`` for every serializer that
    renders, so a resource which only arrives through ``include`` is narrowed down by
    a parameter of its own and must be documented with one.

    See https://jsonapi.org/format/#fetching-sparse-fieldsets
    """

    def setUp(self) -> None:
        self.maxDiff = None
        router = SimpleRouter()
        # songs -> created_by: User is only reachable through a nested include path
        router.register(
            "deep-albums", AlbumWithNestedIncludesViewset, basename="deep-album")
        # songs only: nothing beyond the first include level
        router.register("plain-albums", AlbumModelViewset, basename="plain-album")
        # no included_serializers at all
        router.register("songs", SongModelViewset, basename="song")
        generator = SchemaGenerator(patterns=router.urls)
        self.schema = generator.get_schema(request=None, public=True)
        validate_schema(self.schema)

    def sparse_fieldsets(self, path, schema=None):
        """the `fields[TYPE]` parameters of an operation, keyed by resource type"""
        parameters = (schema or self.schema)["paths"][path]["get"]["parameters"]
        return {
            parameter["name"][len("fields["):-len("]")]: parameter
            for parameter in parameters
            if parameter["name"].startswith("fields[")
        }

    def enum_of(self, parameters, resource_type):
        return parameters[resource_type]["schema"]["items"]["enum"]

    def test_resource_reached_by_a_nested_include_gets_its_own_parameter(self):
        parameters = self.sparse_fieldsets("/deep-albums/")

        self.assertEqual({"Album", "Song", "User"}, set(parameters))
        # the parameter the endpoint answered with is untouched by the fix
        self.assertEqual(
            ['songs', 'title', 'genre', 'year', 'released'],
            self.enum_of(parameters, "Album"))

    def test_included_resource_is_documented_with_its_own_fields(self):
        parameters = self.sparse_fieldsets("/deep-albums/")

        # the enum carries the serializer's fields, in its order; that order is not
        # what a client may or may not send, so it is not what this test is about
        self.assertEqual(
            {'album', 'created_by', 'length', 'title'},
            set(self.enum_of(parameters, "Song")))
        # the id of a resource is rendered whatever a client asks for, so the user's
        # primary key is not a selectable field
        self.assertEqual(['password'], self.enum_of(parameters, "User"))

    def test_first_include_level_alone_is_documented_without_the_second_level(self):
        parameters = self.sparse_fieldsets("/plain-albums/")

        self.assertEqual({"Album", "Song"}, set(parameters))

    def test_endpoint_without_includes_documents_no_foreign_resource(self):
        parameters = self.sparse_fieldsets("/songs/")

        self.assertEqual({"Song"}, set(parameters))

    def test_a_resource_type_reached_twice_is_documented_once(self):
        """the include graph here loops: song -> created_by -> singles -> song"""
        parameters = [
            parameter
            for parameter in self.schema["paths"]["/deep-albums/"]["get"]["parameters"]
            if parameter["name"].startswith("fields[")
        ]
        names = [parameter["name"] for parameter in parameters]

        self.assertEqual(len(names), len(set(names)))
        for parameter in parameters:
            enum = parameter["schema"]["items"]["enum"]
            self.assertEqual(len(enum), len(set(enum)),
                             f"{parameter['name']} documents a field twice")

    def test_an_include_that_cannot_be_resolved_costs_its_own_parameter_only(self):
        """a dotted include path may name a serializer the project cannot import"""

        class AlbumWithUnresolvableIncludeSerializer(
                AlbumWithNestedIncludesSerializer):
            included_serializers = {
                "songs": SongWithCreatorSerializer,
                "phantom": "tests.serializers.ThereIsNoSuchSerializer",
            }

        viewset = AlbumWithNestedIncludesViewset.as_view(
            {"get": "list"},
            serializer_class=AlbumWithUnresolvableIncludeSerializer)
        generator = SchemaGenerator(patterns=[
            path("unresolvable-albums/", viewset, name="unresolvable-album"),
        ])
        schema = generator.get_schema(request=None, public=True)

        # the rest of the graph is documented as if nothing happened, and so is the
        # document itself: only the entry which cannot be loaded is missing
        self.assertEqual(
            {"Album", "Song", "User"},
            set(self.sparse_fieldsets("/unresolvable-albums/", schema)))
        include = next(
            parameter for parameter
            in schema["paths"]["/unresolvable-albums/"]["get"]["parameters"]
            if parameter["name"] == "include")
        self.assertIn("phantom", include["schema"]["items"]["enum"])
        validate_schema(schema)
