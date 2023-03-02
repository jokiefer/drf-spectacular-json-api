from typing import Dict, List, Tuple

from django.utils.translation import gettext_lazy as _
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (build_array_type, build_basic_type,
                                      build_parameter_type, is_serializer)
from rest_framework_json_api.serializers import SparseFieldsetsMixin
from rest_framework_json_api.utils import (format_field_name,
                                           get_resource_name,
                                           get_resource_type_from_serializer)

from drf_spectacular_jsonapi.schemas.plumbing import (
    build_json_api_data_frame, build_json_api_resource_object)
from drf_spectacular_jsonapi.schemas.utils import get_primary_key_of_serializer


class JsonApiAutoSchema(AutoSchema):
    """
    Extend DRF's spectacular AutoSchema for JSON:API serialization.
    """

    #: ignore all the media types and only generate a JSON:API schema.
    content_types = ["application/vnd.api+json"]

    def get_operation(self, path, path_regex, path_prefix, method, registry):
        return super().get_operation(path, path_regex, path_prefix, method, registry)

    def _get_filter_parameters(self) -> Dict:
        """ JSON:API specific handling for sort parameter

        See also json:api docs: https://jsonapi.org/format/#fetching-sorting
        """
        parameters = super()._get_filter_parameters()
        sort_param = next(
            (parameter for parameter in parameters if parameter["name"] == "sort"), None)
        if sort_param and hasattr(self.view, "ordering_fields") and self.view.ordering_fields:
            self._patch_sort_param_schema(sort_param=sort_param)
        elif sort_param:
            # if sorting is not supported by the view, which is identified by the existing of the `ordering_fields` attribute,
            # then the json:api MUST retun 400 Bad Request.

            # So for that case, sorting is not supported for this endpoint. We need to drop the sort filter parameter.
            parameters.pop(parameters.index(sort_param))

        self._patch_translations_for_fields(parameters=parameters)

        return parameters

    def get_label_for_filter(self, filter_obj):
        # explcit title defined by user
        # cast to string to ensure django gettext_lazy is rendered correctly
        return str(filter_obj.label) if filter_obj.label else None

    def get_help_text_for_filter(self, filter_obj):
        # explicit help_text defined by user
        # cast to string to ensure django gettext_lazy is rendered correctly
        return str(filter_obj.help_text) if hasattr(filter_obj, "help_text") and filter_obj.help_text else None

    def get_title_and_description_for_filter_parameter(self, field_name) -> Tuple[str, str]:
        title = None
        description = None
        if hasattr(self.view, "filterset_class"):
            # only in case of filterset classes there is a possibility,
            # that the user set the label or title expliciet to describe what this filter does.
            _filter = self.view.filterset_class.declared_filters.get(
                field_name, None)
            if _filter:
                # only lookup into user specified filters,
                # cause otherwise the title and label are made from the django model stack.
                title = self.get_label_for_filter(filter_obj=_filter)
                description = self.get_help_text_for_filter(
                    filter_obj=_filter)

        return title, description

    def _get_field_name_from_filter_parameter_name(self, parameter_name):
        field_name = parameter_name.split("[")[1].split("]")[0]
        if "_" in field_name:
            field_name = field_name.split("_")[0]
        if "." in field_name:
            field_name = field_name.split(".")[0]
        return field_name

    def _patch_translations_for_fields(self, parameters: Dict):
        """Patching all parameter descriptions with the django translations"""
        for parameter in parameters:
            if "filter[" in parameter.get("name", ""):
                field_name = self._get_field_name_from_filter_parameter_name(
                    parameter_name=parameter["name"])
                title, description = self.get_title_and_description_for_filter_parameter(
                    field_name=field_name)
                if title:
                    parameter["title"] = title
                if description:
                    parameter["description"] = description

    def _patch_sort_param_schema(self, sort_param: Dict) -> None:
        """Patching all possible sortable columns as schema definition."""
        serializer = self._get_serializer()
        enum = []
        if isinstance(self.view.ordering_fields, str) and self.view.ordering_fields == "__all__":
            # All fields can be used to sort
            for field in serializer.fields.values():
                field_name = format_field_name(field.field_name)
                enum.append(field_name)
                enum.append(f"-{field_name}")
        elif isinstance(self.view.ordering_fields, list):
            # only a subset of fields are provided as sortable
            for field_name in self.view.ordering_fields:
                field_name = format_field_name(field_name)
                enum.append(field_name)
                enum.append(f"-{field_name}")
        if enum:
            sort_param["schema"]["type"] = "array"
            sort_param["schema"]["items"] = {"type": "string", "enum": enum}
            sort_param["explode"] = False

    def get_tags(self) -> List[str]:
        # TODO: add a setting wich allows to configure the behaviour?
        return [get_resource_name(context={"view": self.view})]

    def _patch_property_names(self, schema) -> None:
        properties = schema.get("properties", {})
        patched_properties = {}
        for name, field_schema in properties.items():
            json_api_field_name = format_field_name(name)
            patched_properties.update({json_api_field_name: field_schema})
        if properties:
            schema["properties"] = patched_properties

    def _patch_required_names(self, schema) -> None:
        required = schema.get("required", [])
        patched_required = []
        for field_name in required:
            patched_required.append(format_field_name(field_name))
        if required:
            schema["required"] = patched_required

    def _map_basic_serializer(self, serializer, direction):
        """Update field names to match the configured field name formatting configured by the `JSON_API_FORMAT_FIELD_NAMES` setting"""
        schema = super()._map_basic_serializer(serializer, direction)
        self._patch_property_names(schema=schema)
        self._patch_required_names(schema=schema)
        return schema

    def get_include_parameter(self):
        include_parameter = {}
        include_enum = []
        serializer = self._get_serializer()
        if hasattr(serializer, "included_serializers") and serializer.included_serializers:
            include_parameter["include", "query"] = build_parameter_type(
                name="include",
                location="query",
                schema=build_array_type(
                    schema={"type": "string", "enum": include_enum}),
                explode=False,
                description=_(
                    "include query parameter to allow the client to customize which related resources should be returned."),
            )
            for field_name, serializer in serializer.included_serializers.serializers.items():
                include_enum.append(format_field_name(field_name=field_name))
        return include_parameter

    def get_sparse_fieldset_parameters(self):
        serializer = self._get_serializer()
        fields_parameters = {}
        if issubclass(serializer.__class__, SparseFieldsetsMixin):
            # fields parameters are only possible if the used serialzer inherits from `SparseFieldsetsMixin`
            resource_type = get_resource_type_from_serializer(serializer)
            parameter_name = f"fields[{resource_type}]"
            fields_parameters[parameter_name, "query"] = build_parameter_type(
                name=parameter_name,
                location="query",
                schema=build_array_type(schema={"type": "string", "enum": []}),
                explode=False,
                description=_(
                    "endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter."),
            )
            # collect sparrse fieldset and exclude the json:api id field from this lookup
            for field in list(filter(lambda field: (field.field_name != get_primary_key_of_serializer(serializer)), serializer.fields.values())):
                fields_parameters[parameter_name, "query"]["schema"]["items"]["enum"].append(
                    format_field_name(field.field_name))
        # TODO: sparse fieldset values for included serializers are also needed
        return fields_parameters

    def _process_override_parameters(self, direction="request"):
        """Dirty hack to push in json:api specific parameters"""
        result = super()._process_override_parameters(direction=direction)

        if self.view.request.method == "GET":
            # only needed on http get method
            result = result | self.get_include_parameter()
            result = result | self.get_sparse_fieldset_parameters()
        return result

    def _map_basic_serializer(self, serializer, direction):
        object_schema = super()._map_basic_serializer(
            serializer=serializer, direction=direction)
        json_api_object_schema = build_json_api_resource_object(
            object_schema, serializer, method=self.method)
        return json_api_object_schema

    def _postprocess_serializer_schema(self, schema, serializer, direction):
        if is_serializer(serializer):
            schema = build_json_api_data_frame(schema)
        return super()._postprocess_serializer_schema(schema, serializer, direction)
