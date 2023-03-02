from django.utils.translation import gettext_lazy as _
from rest_framework.fields import empty
from rest_framework_json_api import serializers
from rest_framework_json_api.utils import (format_field_name,
                                           get_related_resource_type,
                                           get_resource_type_from_serializer)

from drf_spectacular_jsonapi.schemas.utils import get_primary_key_of_serializer


def build_json_api_relationship_object(field):
    schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                # TODO: could also provide the correct id format
                "description": _("The identifier of the related object.")
            },
            "type": {
                "type": "string",
                "description": _(""),
                "enum": [get_related_resource_type(field)]
            }
        },
        "required": ["id", "type"],
    }

    if field.read_only:
        schema["readOnly"] = True
    if field.write_only:
        schema["writeOnly"] = True
    if field.allow_null:
        schema["nullable"] = True
    if field.default and field.default != empty:
        schema["default"] = field.default
    if field.help_text:
        # Ensure django gettext_lazy is rendered correctly
        schema["description"] = str(field.help_text)

    return schema


def build_json_api_data_frame(schema):
    return {
        "type": "object",
        "properties": {
            "data": schema
        },
        "required": ["data"]
    }


def build_json_api_resource_object(schema, serializer, method):
    required = []
    attributes = {}
    relationships = {}
    resource_object_schema = {
        "type": "object",
        "required": ["type"],
        "additionalProperties": False,
        "properties": {
            "type": {
                "type": "string",
                "description": _("The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."),
                "enum": [get_resource_type_from_serializer(serializer=serializer)]
            },
            # TODO:
            # "links": {
            #     "type": "object",
            #     "properties": {"self": {"$ref": "#/components/schemas/link"}},
            # },
        },
    }
    pk_name = get_primary_key_of_serializer(serializer=serializer)

    if method == "PATCH" or method == "GET" or pk_name and method == "POST" and not serializer.fields[pk_name].read_only:
        # case 1: PATCH:
        # The PATCH request MUST include a single resource object as primary data.
        # The resource object MUST contain type and id members.

        # case 2: "GET"
        # If method == "GET" this resource object schema shall be build for an response body schema definition.
        # id is required

        # case 3: "POST" with client id see: https://jsonapi.org/format/#crud-creating-client-ids
        resource_object_schema["required"].append("id")

        # {} is a shorthand syntax for an arbitrary-type: see https://swagger.io/docs/specification/data-models/data-types/#any
        resource_object_schema["properties"]["id"] = schema["properties"][pk_name] if pk_name else {
        }

        is_read_only = resource_object_schema["properties"]["id"].get(
            "readOnly", None)
        if is_read_only:
            del resource_object_schema["properties"]["id"]["readOnly"]

    for field in serializer.fields.values():
        field_schema = schema["properties"][field.field_name]
        if field.field_name == pk_name:
            # id field shall not be part of the attributes
            continue
        if isinstance(field, serializers.HyperlinkedIdentityField):
            # the 'url' is not an attribute but rather a self.link, so don't map it here.
            continue
        if isinstance(field, serializers.HiddenField):
            continue
        if isinstance(field, serializers.RelatedField):
            relationships[format_field_name(
                field.field_name)] = build_json_api_data_frame(build_json_api_relationship_object(field))
            continue
        if isinstance(field, serializers.ManyRelatedField):
            relationships[format_field_name(field.field_name)] = build_json_api_data_frame({
                "type": "array",
                "items": build_json_api_relationship_object(field)
            })
            continue

        if field.required:
            required.append(format_field_name(field.field_name))

        if field.help_text:
            # Ensure django gettext_lazy is rendered correctly
            field_schema["description"] = str(field.help_text)

        attributes[format_field_name(field.field_name)] = field_schema

    if attributes:
        resource_object_schema["properties"]["attributes"] = {
            "type": "object",
            "properties": attributes,
        }
        if required:
            resource_object_schema["properties"]["attributes"]["required"] = required

    if relationships:
        resource_object_schema["properties"]["relationships"] = {
            "type": "object",
            "properties": relationships,
        }

    return resource_object_schema
