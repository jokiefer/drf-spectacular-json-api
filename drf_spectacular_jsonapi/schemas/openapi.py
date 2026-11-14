from typing import Any, Dict, List, Tuple

from django.db.models.fields.related import (ForeignKey, ManyToManyField,
                                             OneToOneField)
from django.db.models.fields.reverse_related import (ManyToManyRel,
                                                     ManyToOneRel)
from django.utils.translation import gettext_lazy as _
from drf_spectacular.contrib.django_filters import DjangoFilterExtension
from drf_spectacular.drainage import warn
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import (ResolvedComponent, build_array_type,
                                      build_parameter_type, force_instance,
                                      is_list_serializer)
from rest_framework.serializers import BaseSerializer
from rest_framework_json_api.serializers import \
    ModelSerializer as JsonApiModelSerializer
from rest_framework_json_api.serializers import (
    ResourceIdentifierObjectSerializer, SparseFieldsetsMixin)
from rest_framework_json_api.utils import (format_field_name,
                                           format_link_segment,
                                           get_resource_name,
                                           get_resource_type_from_model,
                                           get_resource_type_from_serializer)
from rest_framework_json_api.views import RelationshipView

from drf_spectacular_jsonapi.schemas.converters import JsonApiResourceObject
from drf_spectacular_jsonapi.schemas.plumbing import build_json_api_data_frame
from drf_spectacular_jsonapi.schemas.utils import get_serializer_pk_field_name


class DjangoJsonApiFilterExtension(DjangoFilterExtension):
    target_class = 'rest_framework_json_api.django_filters.backends.DjangoFilterBackend'
    priority = 1

    def resolve_filter_field(self, *args, **kwargs):
        result = super().resolve_filter_field(*args, **kwargs)
        for item in result:
            name = item["name"]
            if "filter[" not in name:
                name = f"filter[{name}]"
                item["name"] = name
        return result


class JsonApiAutoSchema(AutoSchema):
    """
    Extend DRF's spectacular AutoSchema for JSON:API serialization.
    """

    #: ignore all the media types and only generate a JSON:API schema.
    content_types = ["application/vnd.api+json"]

    json_api_resource_object_converter_class = JsonApiResourceObject

    def get_json_api_resource_object_converter_class(self):
        return self.json_api_resource_object_converter_class

    def is_json_api_resource_serializer(self, serializer: Any) -> bool:
        """Return True if *serializer* is documented as a JSON:API resource object.

        Resource objects carry ``type``, optional ``id``, ``attributes``, and
        ``relationships`` per https://jsonapi.org/format/#document-resource-objects.
        Plain nested objects used only inside ``attributes`` stay as regular
        JSON Schema objects.

        Default rules (override in a subclass for custom classification):

        - ``rest_framework_json_api.serializers.ModelSerializer`` subclasses
          are treated as resources (backward compatible with existing schemas).
        - Serializers whose ``Meta.resource_name`` is set are treated as
          resources (explicit opt-in for non-model serializers).
        - Other serializers (for example plain ``rest_framework.serializers.Serializer``)
          are treated as inline attribute objects.
        """
        serializer = force_instance(serializer)
        if is_list_serializer(serializer):
            serializer = serializer.child
        meta = getattr(serializer, "Meta", None)
        if meta is not None and getattr(meta, "resource_name", None):
            return True
        return isinstance(serializer, JsonApiModelSerializer)

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
                    # the Parameter Object has no "title" member (OAS 3.0
                    # forbids it there and spec validators reject the whole
                    # document); the Schema Object does, and the title
                    # belongs to the value the parameter carries anyway.
                    schema = parameter.setdefault("schema", {})
                    schema["title"] = title
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
        if isinstance(self.view, RelationshipView):
            # RelationshipViews are generic based on the passed `related_field`.
            # So to fully support all the possible related fields, we need to analyze them to get the correct related resource name

            # 1. get all possible related_field parameters
            # 2. based on the possible related_field parameters (json:api ressources) build the tag array
            # two relations can point at the same resource type, and a view may offer
            # one relation under two segments; a type is tagged once
            return list(dict.fromkeys(
                get_resource_type_from_model(field.related_model)
                for name, field in self._get_relationship_fields()
            )) + ['RelationshipViews']
        else:
            return [get_resource_name(context={"view": self.view})]

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

    def get_included_serializers(self, serializer) -> List[Any]:
        """Every serializer an ``include`` can add to the document of *serializer*.

        ``include`` paths may nest (``include=author.organization``) and the runtime
        accepts them by walking down each serializer's own ``included_serializers``
        (:meth:`rest_framework_json_api.filters.IncludedResourcesFilter._validate_path`),
        so the resource types a client may address are the transitive closure of that
        mapping. A serializer is visited once, which is what makes a cycle such as
        ``song -> created_by -> singles -> song`` terminate.

        Entries are read through the mapping itself: ``included_serializers`` is a
        :class:`rest_framework_json_api.serializers.LazySerializersDict` whose values
        may be a serializer class, the string ``"self"`` or a dotted import path, and
        only ``__getitem__`` resolves all three the way the runtime does.
        """
        collected: List[Any] = []
        seen = set()

        def walk(current):
            included = getattr(current, "included_serializers", None)
            if not included:
                return
            for field_name in included:
                try:
                    included_serializer = force_instance(included[field_name])
                except (ImportError, AttributeError, TypeError) as error:
                    # an entry the application could not load itself, were this
                    # include path used; the rest of the document stays correct
                    warn(f"included serializer of '{field_name}' could not be "
                         f"resolved and is not documented: {error}")
                    continue
                if not isinstance(included_serializer, BaseSerializer):
                    # an unresolved entry, e.g. a "self" of a plain dict
                    continue
                if included_serializer.__class__ in seen:
                    # already collected through another include path
                    continue
                seen.add(included_serializer.__class__)
                collected.append(included_serializer)
                walk(included_serializer)

        walk(serializer)
        return collected

    def get_sparse_fieldset_field_names(self, serializer) -> List[str]:
        """The field names a ``fields[TYPE]`` value may carry for *serializer*.

        The json:api ``id`` is rendered whatever a client asks for, so it is not part
        of the selectable set - the same rule the view's own serializer follows.
        """
        return [
            format_field_name(field.field_name)
            for field in serializer.fields.values()
            if field.field_name != get_serializer_pk_field_name(serializer)
        ]

    def _add_sparse_fieldset_parameter(self, fields_parameters, serializer) -> None:
        """Document ``fields[<resource type>]`` for one serializer of the document."""
        if not isinstance(serializer, SparseFieldsetsMixin):
            # fields parameters are only possible if the used serializer inherits
            # from `SparseFieldsetsMixin`, because only that one reads the parameter
            return
        try:
            resource_type = get_resource_type_from_serializer(serializer)
        except AttributeError:
            # a serializer without a resource type is a plain nested object and never
            # appears in the document as a resource of its own
            return

        parameter_name = f"fields[{resource_type}]"
        parameter = fields_parameters.get((parameter_name, "query"))
        if parameter is None:
            parameter = build_parameter_type(
                name=parameter_name,
                location="query",
                schema=build_array_type(schema={"type": "string", "enum": []}),
                explode=False,
                description=_(
                    "endpoint return only specific fields in the response on a per-type basis by including a fields[TYPE] query parameter."),
            )
            fields_parameters[parameter_name, "query"] = parameter

        # more than one include path can reach the same resource type through
        # different serializers; the parameter is the union of what they accept
        enum = parameter["schema"]["items"]["enum"]
        for field_name in self.get_sparse_fieldset_field_names(serializer):
            if field_name not in enum:
                enum.append(field_name)

    def get_sparse_fieldset_parameters(self):
        """Sparse fieldset parameters of everything the response can contain.

        See https://jsonapi.org/format/#fetching-sparse-fieldsets: ``fields[TYPE]``
        is keyed by resource type, not by the resource the endpoint answers, and
        :class:`rest_framework_json_api.serializers.SparseFieldsetsMixin` applies it
        to every serializer that renders - so an included resource is sparse
        fielded under its own type as well.
        """
        serializer = self._get_serializer()
        fields_parameters = {}
        # the resource the endpoint answers ...
        self._add_sparse_fieldset_parameter(fields_parameters, serializer)
        # ... and every resource an `include` can add next to it
        for included_serializer in self.get_included_serializers(serializer):
            self._add_sparse_fieldset_parameter(fields_parameters, included_serializer)
        return fields_parameters

    def _process_override_parameters(self, direction="request"):
        """Dirty hack to push in json:api specific parameters"""
        result = super()._process_override_parameters(direction=direction)

        if self.view.request.method == "GET":
            # only needed on http get method
            result = result | self.get_include_parameter()
            result = result | self.get_sparse_fieldset_parameters()
        return result

    def _get_serializer_name(self, serializer, direction, bypass_extensions=False):
        if isinstance(serializer, ResourceIdentifierObjectSerializer) and isinstance(self.view, RelationshipView):
            resource_name = get_resource_type_from_model(
                self.view.queryset.model)
            return f"{resource_name}RelationShips"

        return super()._get_serializer_name(serializer, direction, bypass_extensions)

    def _map_serializer(self, serializer, direction, bypass_extensions=False):
        if isinstance(serializer, ResourceIdentifierObjectSerializer):
            one_of = []

            related_fields = self._get_relationship_fields()

            for name, field in related_fields:
                resource_name = get_resource_type_from_model(
                    field.related_model)

                related_model_instance = field.related_model()
                fields = related_model_instance._meta.fields
                pk_field = next((field for field in fields if field.name ==
                                related_model_instance._meta.pk.name), fields)

                schema = {
                    "type": "object",
                    "required": ["type"],
                    "additionalProperties": False,
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": _("The [type](https://jsonapi.org/format/#document-resource-object-identification) member is used to describe resource objects that share common attributes and relationships."),
                            "enum": [resource_name]
                        },
                        "id": self._map_model_field(pk_field, direction)
                        # TODO:
                        # "links": {
                        #     "type": "object",
                        #     "properties": {"self": {"$ref": "#/components/schemas/link"}},
                        # },
                    },
                }
                if isinstance(field, (ManyToManyField, ManyToOneRel, ManyToManyRel)):
                    one_of.append({
                        "type": "array",
                        "items": schema,
                    })
                else:
                    one_of.append(schema)

            return {
                "oneOf": one_of
            }

        return super()._map_serializer(serializer, direction, bypass_extensions)

    def _map_basic_serializer(self, serializer, direction):
        # let drf_spectacular do the default drf_spectacular stuff first.
        # It is an performace leak, but for now the only handy way without copy paste all the drf_spectacular code.
        object_schema = super()._map_basic_serializer(
            serializer=serializer, direction=direction)

        if not self.is_json_api_resource_serializer(serializer):
            return object_schema

        json_api_resource_object_schema = self.get_json_api_resource_object_converter_class()(
            serializer=serializer,
            drf_spectactular_schema=object_schema,
            method=self.method,
        ).__dict__()
        return json_api_resource_object_schema

    def _postprocess_serializer_schema(self, schema, serializer, direction):
        schema = super()._postprocess_serializer_schema(schema, serializer, direction)

        if direction == "response":
            # responses shall not be framed.
            # it is handled by the _get_response_for_code function
            pass
        elif self.is_json_api_resource_serializer(serializer):
            schema = build_json_api_data_frame(schema)
        return schema

    def _get_response_for_code(self, serializer, status_code, media_types=None, direction='response'):
        response = super()._get_response_for_code(
            serializer, status_code, media_types, direction)
        content = response.get("content")
        if content and "application/vnd.api+json" in content and "Paginated" not in content["application/vnd.api+json"]["schema"]["$ref"]:
            response_component = ResolvedComponent(
                name=self._get_serializer_name(
                    serializer=serializer, direction=direction)+"Response",
                type=ResolvedComponent.SCHEMA,
                schema=build_json_api_data_frame(
                    content["application/vnd.api+json"]["schema"]),
                object=serializer.child if is_list_serializer(
                    serializer) else serializer
            )
            self.registry.register_on_missing(response_component)
            content["application/vnd.api+json"]["schema"] = response_component.ref
        return response

    def _get_relationship_fields(self):
        """The relation names of the view's model, spelled as the URL asks for them.

        :meth:`rest_framework_json_api.views.RelationshipView.get_related_instance`
        resolves the path segment against an instance of the model::

            getattr(self.get_object(), self.get_related_field_name())

        and an attribute it does not find is a 404. So the only names which may be
        documented as this view's ``related_field`` enum are the model's own attribute
        names, transformed by :func:`rest_framework_json_api.utils.format_link_segment`
        - the inverse of the ``undo_format_link_segment`` the view applies to what the
        client sent. Any other spelling is a documented value the server refuses.
        """
        base_model = self.view.queryset.model()
        relations = {}

        # local relation fields: a field's name is the attribute it is reached by
        for field in base_model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField, ManyToManyField)):
                relations[field.name] = field

        # reverse relations: explicitly not the keys of `_meta.fields_map`, which are
        # the *query* names and agree with the accessor only by accident. `Song.album`
        # declares `related_name = "singles"` and `related_query_name = "single"`, so
        # the relation is reached as `album.singles` and filtered as
        # `Song.objects.filter(single=...)` - of the two, only the first is an
        # attribute the view can resolve.
        for relation in base_model._meta.related_objects:
            if getattr(relation, "parent_link", False):
                # the link of a multi table inheritance child: declared by the child,
                # so it is an attribute of the child, never of the model documented here
                continue
            accessor_name = relation.get_accessor_name()
            if accessor_name.startswith("+"):
                # `related_name="+"` keeps the relation off the reverse side, which
                # leaves no attribute to address and therefore no relationship
                continue
            relations[accessor_name] = relation

        related_fields = [
            (format_link_segment(attribute), relation)
            for attribute, relation in relations.items()
        ]

        # a view may offer an attribute under another segment; the mapping is spelled
        # {segment: attribute} and is consulted before the name is used as an attribute
        for segment, attribute in self.view.field_name_mapping.items():
            if attribute in relations:
                related_fields.append((format_link_segment(segment), relations[attribute]))

        return related_fields

    def _resolve_path_parameters(self, variables):
        params = super()._resolve_path_parameters(variables)
        if isinstance(self.view, RelationshipView):
            related_fields = self._get_relationship_fields()

            # TODO: there is a function `self.view.get_related_field_name` which returns the concrete name of the related_field
            # But it will only works if the view is initialized with correct kwargs.
            related_field_parameter = next(
                (param for param in params if param["name"] == "related_field"), params)
            related_field_parameter["schema"]["enum"] = list(dict.fromkeys(
                name for name, field in related_fields))
            related_field_parameter["description"] = _(
                "Pass in one of the possible relation types to get all related objects.")

        return params
