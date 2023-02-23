from django.utils.translation import gettext_lazy as _
from rest_framework.fields import empty
from rest_framework_json_api import serializers
from rest_framework_json_api.utils import (format_field_name,
                                           get_related_resource_type,
                                           get_resource_type_from_serializer)


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
    result = {
        "type": "object",
        "required": ["type", "id"],
        "additionalProperties": False,
        "properties": {
            "type": {
                "type": "string",
                "description": _("The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."),
                "enum": [get_resource_type_from_serializer(serializer=serializer)]
            },
            "id": schema["properties"]["id"],
            # TODO:
            # "links": {
            #     "type": "object",
            #     "properties": {"self": {"$ref": "#/components/schemas/link"}},
            # },
        },
    }

    if method == "POST" and serializer.fields["id"].read_only:
        # no id is needed on creating resources. Exception: https://jsonapi.org/format/#crud-creating-client-ids
        result["required"].remove("id")
        del result["properties"]["id"]
    elif method == "POST" and not serializer.fields["id"].read_only or method == "PATCH":
        # id is required
        del result["properties"]["id"]["readOnly"]

    for field in serializer.fields.values():
        field_schema = schema["properties"][field.field_name]
        if field.field_name == "id":
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
        result["properties"]["attributes"] = {
            "type": "object",
            "properties": attributes,
        }
        if required:
            result["properties"]["attributes"]["required"] = required

    if relationships:
        result["properties"]["relationships"] = {
            "type": "object",
            "properties": relationships,
        }

    return result
