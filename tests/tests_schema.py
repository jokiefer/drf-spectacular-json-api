from django.test.testcases import SimpleTestCase
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema


class SimpleSchemaTestCase(SimpleTestCase):

    def ordered(self, obj):
        # don't know why, but enum values are generated in different order in different runs
        # so we order them before comparing them to get reproduceable tests
        if isinstance(obj, dict):
            return sorted((k, self.ordered(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.ordered(x) for x in obj)
        if isinstance(obj, str):
            obj.replace("\n", "")
        return obj

    def setUp(self) -> None:
        self.maxDiff = None
        generator = SchemaGenerator()
        self.schema = generator.get_schema(request=None, public=True)
        # make sure generated schemas are always valid
        validate_schema(self.schema)


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

    def test_get_response_body(self):
        self.assertEqual(
            self.schema["paths"]["/albums/"]["get"]["responses"]["200"]["content"]["application/vnd.api+json"]["schema"]["$ref"],
            "#/components/schemas/PaginatedAlbumList"
        )
        self.assertEqual(
            self.schema["components"]["schemas"]["PaginatedAlbumList"]["properties"]["data"]["items"]["$ref"],
            "#/components/schemas/Album"
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
        )
        self.assertEqual(expected, calculated)

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
                                        "title": "Resource Identifier",
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
                                        "title": "Resource Identifier",
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


class TestSchemaOutputForNestedResources(SimpleSchemaTestCase):
    def test_nested_path_parameter_fix(self):
        calculated = self.ordered(
            self.schema["paths"]["/albums/{AlbumId}/songs/"]["get"]["parameters"])        
        expected = self.ordered(
            [
                [('description', 'A page number within the paginated result set.'), ('in', 'query'), ('name', 'page[number]'), ('required', False), ('schema', [('type', 'integer')])], 
                [('description', 'A search term.'), ('in', 'query'), ('name', 'filter[search]'), ('required', False), ('schema', [('type', 'string')])], 
                [('description', 'Number of results to return per page.'), ('in', 'query'), ('name', 'page[size]'), ('required', False), ('schema', [('type', 'integer')])], 
                [('description', 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.'), ('explode', False), ('in', 'query'), ('name', 'fields[Song]'), ('schema', [('items', [('enum', ['album', 'created_by', 'length', 'title']), ('type', 'string')]), ('type', 'array')])], 
                [('in', 'path'), ('name', 'AlbumId'), ('required', True), ('schema', [('type', 'string')])]]
        )
        self.assertEqual(expected, calculated)
        

    def test_nested_path_parameter_fix(self):
        f = open("demofile2.txt", "a")
        f.write(str(self.schema))
        f.close()
        calculated = self.ordered(
            self.schema["paths"]["/albums/{AlbumId}/songs-as-view/"]["get"]["parameters"])        
        
       
        expected = self.ordered(
            [
                [('description', 'A page number within the paginated result set.'), ('in', 'query'), ('name', 'page[number]'), ('required', False), ('schema', [('type', 'integer')])], 
                [('description', 'A search term.'), ('in', 'query'), ('name', 'filter[search]'), ('required', False), ('schema', [('type', 'string')])], 
                [('description', 'Number of results to return per page.'), ('in', 'query'), ('name', 'page[size]'), ('required', False), ('schema', [('type', 'integer')])], 
                [('description', 'endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter.'), ('explode', False), ('in', 'query'), ('name', 'fields[Song]'), ('schema', [('items', [('enum', ['album', 'created_by', 'length', 'title']), ('type', 'string')]), ('type', 'array')])], 
                [('in', 'path'), ('name', 'AlbumId'), ('required', True), ('schema', [('type', 'string')])]]
        )
        self.assertEqual(expected, calculated)
        