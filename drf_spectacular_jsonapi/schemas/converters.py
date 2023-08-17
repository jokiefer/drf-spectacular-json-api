from typing import Dict

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import Field
from rest_framework_json_api.serializers import (HiddenField,
                                                 HyperlinkedIdentityField,
                                                 ManyRelatedField,
                                                 ModelSerializer, RelatedField)
from rest_framework_json_api.utils import (format_field_name,
                                           get_related_resource_type,
                                           get_resource_type_from_serializer)

from drf_spectacular_jsonapi.schemas.plumbing import build_json_api_data_frame
from drf_spectacular_jsonapi.schemas.utils import get_primary_key_of_serializer


class JsonApiRelationshipObject:
    """Converter class to convert drf_spectacular schema of related fields as json:api specific related field schema"""

    def __init__(self, field: Field, drf_spectactular_field_schema: Dict) -> None:
        self.field = field
        self.drf_spectacular_field_schema = drf_spectactular_field_schema
        self.related_resource_type = get_related_resource_type(self.field)
        self._schema = {
            "type": "object",
            "properties": {
                "id": {},
                "type": {"type": "string"}
            },
            "required": ["id", "type"],
        }
        self._schema_meta = {}
        self.patch()

    def get_id_title(self):
        return _("Resource Identifier")

    def get_id_description(self):
        return _("The identifier of the related object.")

    def patch_id_metadata(self):
        self._schema["properties"]["id"]["title"] = self.get_id_title()
        self._schema["properties"]["id"]["description"] = self.get_id_description()

    def get_default_relation_description(self):
        return _("A related resource object from type %(type)s") % {"type": self.related_resource_type}

    def get_default_relation_title(self):
        return self.related_resource_type

    def patch_id(self) -> None:
        """"""
        # drf_spectacular still discovered the related id schema, but with all information of the serializer field
        # we need to move the metadata information on a higher level to describe the relation and not the data
        self._schema["properties"]["id"] = self.drf_spectacular_field_schema[
            "items"] if self.drf_spectacular_field_schema["type"] == "array" else self.drf_spectacular_field_schema
        self.patch_id_metadata()

        self._schema_meta.update({"description": self.drf_spectacular_field_schema.pop(
            "description", self.get_default_relation_description())})
        self._schema_meta.update({"title": self.drf_spectacular_field_schema.pop(
            "title", self.get_default_relation_title())})
        
        if "readOnly" in self.drf_spectacular_field_schema:
            self._schema_meta.update({"readOnly": self.drf_spectacular_field_schema.pop("readOnly")})
        
        if "nullable" in self.drf_spectacular_field_schema:
            self._schema_meta.update({"nullable": self.drf_spectacular_field_schema.pop("nullable")})


    def patch_type_enum(self) -> None:
        """Resolve the resource type of the serializer and sets the type enum of the resource object schema"""
        self._schema["properties"]["type"].update(
            {"enum": [self.related_resource_type]})

    def get_type_title(self):
        return _("Resource Type Name")

    def get_type_description(self):
        return _("The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships.")

    def patch_type_metadata(self):
        self._schema["properties"]["type"]["title"] = self.get_type_title()
        self._schema["properties"]["type"]["description"] = self.get_type_description()

    def patch_type(self) -> None:
        self.patch_type_enum()
        self.patch_type_metadata()

    def patch_root_metadata(self) -> None:
        self._schema = self._schema | self._schema_meta

    def patch(self) -> None:
        self.patch_id()
        self.patch_type()

        if isinstance(self.field, ManyRelatedField):
            self._schema = {
                "type": "array",
                "items": self._schema
            }

        self._schema = build_json_api_data_frame(self._schema)

        self.patch_root_metadata()

    def __dict__(self):
        return self._schema


class JsonApiResourceObject:
    """Converter class for convertig drf_spectaclar schema to specific json:api resource object schema"""

    related_field_converter_class = JsonApiRelationshipObject

    def __init__(self, serializer: ModelSerializer, drf_spectactular_schema: Dict, method: str) -> None:
        self.serializer = serializer
        self.drf_spectacular_schema = drf_spectactular_schema
        self.method = method

        self._schema = {
            "type": "object",
            "required": ["type"],
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": _("The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."),
                },
                # TODO:
                # "links": {
                #     "type": "object",
                #     "properties": {"self": {"$ref": "#/components/schemas/link"}},
                # },
            },
        }
        self.pk_name = get_primary_key_of_serializer(
            serializer=self.serializer)

        self.patch()

    def patch(self):
        self._patch_type_enum()
        self._patch_id_for_json_api_resource_object()
        self._split_into_attributes_and_relationships()

    def get_related_field_converter_class(self):
        return self.related_field_converter_class

    def _patch_type_enum(self) -> None:
        """Resolve the resource type of the serializer and sets the type enum of the resource object schema"""
        self._schema["properties"]["type"]["enum"] = [
            get_resource_type_from_serializer(serializer=self.serializer)]

    def _patch_id_for_json_api_resource_object(self) -> None:
        """Patches the `drf_spectacular_jsonapi.schemas.models.JsonApiResourceObject._resource_object_schema` with the correct `id` property."""
        if self.method == "PATCH" or self.method == "GET" or self.pk_name and self.method == "POST" and not self.serializer.fields[self.pk_name].read_only:
            # case 1: PATCH:
            # The PATCH request MUST include a single resource object as primary data.
            # The resource object MUST contain type and id members.

            # case 2: "GET"
            # If method == "GET" this resource object schema shall be build for an response body schema definition.
            # id is required

            # case 3: "POST" with client id see: https://jsonapi.org/format/#crud-creating-client-ids
            self._schema["required"].append(
                "id") if "id" not in self._schema["required"] else None

            # {} is a shorthand syntax for an arbitrary-type: see https://swagger.io/docs/specification/data-models/data-types/#any
            self._schema["properties"]["id"] = self.drf_spectacular_schema["properties"][self.pk_name] if self.pk_name else {
            }

            is_read_only = self._schema["properties"]["id"].get(
                "readOnly", None)
            if is_read_only:
                del self._schema["properties"]["id"]["readOnly"]

    def _split_into_attributes_and_relationships(self):
        attributes = {}
        required_attributes = []

        relationships = {}
        required_relationships = []
        # sorts the serializer fields in attributes and relationships to match the json:api resource object schema
        for field in self.serializer.fields.values():
            # https://jsonapi.org/format/#document-resource-objects
            if field.field_name == self.pk_name:
                # id field shall not be part of the attributes
                continue
            if isinstance(field, (HyperlinkedIdentityField, HiddenField)):
                # the 'url' is not an attribute but rather a self.link, so don't map it here.
                # TODO: shall hidden fields be part of the schema?
                continue

            if isinstance(field, RelatedField) or isinstance(field, ManyRelatedField):
                relationships[format_field_name(
                    field.field_name)] = self.get_related_field_converter_class()(field=field, drf_spectactular_field_schema=self.drf_spectacular_schema["properties"][field.field_name]).__dict__()
                if field.required:
                    required_relationships.append(format_field_name(field.field_name))
                continue

            if field.required:
                required_attributes.append(format_field_name(field.field_name))

            attributes[format_field_name(
                field.field_name)] = self.drf_spectacular_schema["properties"][field.field_name]

        if attributes:
            self._schema["properties"]["attributes"] = {
                "type": "object",
                "properties": attributes,
            }
            if required_attributes:
                self._schema["properties"]["attributes"]["required"] = required_attributes

        if relationships:
            self._schema["properties"]["relationships"] = {
                "type": "object",
                "properties": relationships,
            }
            if required_relationships:
                self._schema["properties"]["relationships"]["required"] = required_relationships

    def __dict__(self) -> Dict:
        return self._schema
