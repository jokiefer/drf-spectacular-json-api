from django.test.testcases import SimpleTestCase
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema

from .urls import urlpatterns


class SimpleSchemaTestCase(SimpleTestCase):
    def ordered(self, obj):
        # don't know why, but enum values are generated in different order in different runs
        # so we order them before comparing them to get reproduceable tests
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        else:
            return obj

    def setUp(self) -> None:
        generator = SchemaGenerator()
        self.schema = generator.get_schema(request=None, public=True)
        # make sure generated schemas are always valid
        validate_schema(self.schema)


class TestSchemaOutputForSimpleModelSerializer(SimpleSchemaTestCase):

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
                'description': 'Which field to use when ordering the results.',
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
                'required': False,
                'description': 'genre',
                'schema': {'type': 'string', 'enum': ["POP", "ROCK"]}
            },
            {
                'in': 'query',
                'name': 'filter[title.contains]',
                'required': False,
                'description': 'title__contains',
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

        calculated = self.ordered(
            self.schema["components"]["schemas"]["AlbumRequest"])
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
                            "attributes": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "The title of the Album",
                                        # TODO: "title": "Title"
                                        "maxLength": 100,
                                        "minLength": 1,
                                    },
                                    "genre": {
                                        "type": "string",
                                        "enum": ["POP", "ROCK"],
                                        "description": "Wich kind of genre this Album represents"
                                    },
                                    "year": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648,
                                        "description": "The release year"
                                    },
                                    "released": {
                                        "type": "boolean",
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
                                                            # TODO: the format of the id
                                                            "description": "The identifier of the related object."
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "description": "",
                                                            "enum": ["Song"]
                                                        }
                                                    },
                                                    "required": ["id", "type"],
                                                    "description": "The songs which are part of this album.",
                                                    # TODO: "title": "Songs"
                                                },
                                            }
                                        },
                                        "required": ["data"]
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
        )
        self.assertEqual(expected, calculated)

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
                                        "description": "The title of the Album",
                                        # TODO: "title": "Title"
                                        "maxLength": 100,
                                        "minLength": 1,
                                    },
                                    "genre": {
                                        "type": "string",
                                        "enum": ["POP", "ROCK"],
                                        "description": "Wich kind of genre this Album represents"
                                    },
                                    "year": {
                                        "type": "integer",
                                        "maximum": 2147483647,
                                        "minimum": -2147483648,
                                        "description": "The release year"
                                    },
                                    "released": {
                                        "type": "boolean",
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
                                                            # TODO: the format of the id
                                                            "description": "The identifier of the related object."
                                                        },
                                                        "type": {
                                                            "type": "string",
                                                            "description": "",
                                                            "enum": ["Song"]
                                                        }
                                                    },
                                                    "required": ["id", "type"],
                                                    "description": "The songs which are part of this album.",
                                                    # TODO: "title": "Songs"
                                                },
                                            }
                                        },
                                        "required": ["data"]
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
