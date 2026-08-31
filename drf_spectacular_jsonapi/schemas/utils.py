from django.core.exceptions import FieldDoesNotExist
from django.db import models
from rest_framework import serializers


def get_model_field(model: type[models.Model], name: str) -> models.Field:
    """
    Resolve a Django model field by either its `name` or `attname`.

    Examples:
        field.name    == "group_ptr"
        field.attname == "group_ptr_id"
    """
    try:
        return model._meta.get_field(name)
    except FieldDoesNotExist:
        pass

    for field in model._meta.get_fields():
        if getattr(field, "attname", None) == name:
            return field

    raise FieldDoesNotExist(
        f"{model.__name__} has no field or field attname {name!r}"
    )


def resolve_source_field(
    model: type[models.Model],
    source: str,
) -> models.Field | None:
    """
    Resolve a DRF serializer source to the final Django model field.

    Examples:
        "id"
        "group_ptr"
        "group_ptr_id"
        "group_ptr.id"

    Returns None when the source cannot be resolved through Django model
    fields, e.g. for @property, method based fields, source="*", etc.
    """
    if not source or source == "*":
        return None

    current_model = model
    resolved_field = None

    for part in source.split("."):
        try:
            resolved_field = get_model_field(current_model, part)
        except FieldDoesNotExist:
            return None

        if resolved_field.is_relation:
            related_model = getattr(resolved_field, "related_model", None)

            if related_model is not None:
                current_model = related_model

    return resolved_field


def normalize_pk_field(field: models.Field) -> models.Field:
    """
    Follow Django multi-table inheritance parent links until the underlying
    non-parent-link PK field is reached.

    Example:

        SpecialGroup.group_ptr
            -> Group.id
    """
    while (
        getattr(field, "remote_field", None) is not None
        and getattr(field.remote_field, "parent_link", False)
    ):
        field = field.target_field

    return field


def is_same_pk_field(
    field: models.Field,
    pk_field: models.Field,
) -> bool:
    """
    Compare model fields after normalizing multi-table inheritance PK links.
    """
    field = normalize_pk_field(field)
    pk_field = normalize_pk_field(pk_field)

    return field == pk_field


def get_serializer_pk_field(
    serializer: serializers.ModelSerializer,
) -> tuple[str, serializers.Field] | None:
    """
    Find the serializer field that represents the model's primary key.

    Works with:
      - regular primary keys
      - custom / UUID primary keys
      - multi-table inheritance
      - renamed serializer fields
      - source="..."
      - ForeignKey / OneToOneField attnames such as "group_ptr_id"

    Returns:
        (serializer_field_name, serializer_field)

    or:
        None
    """

    try:
        model = serializer.Meta.model
        model_pk = model._meta.pk

        for field_name, serializer_field in serializer.fields.items():

            # Once a DRF field is bound, `source` normally already contains
            # field_name when no explicit source was specified.
            source = serializer_field.source or field_name

            model_field = resolve_source_field(model, source)

            if model_field is None:
                continue

            if is_same_pk_field(model_field, model_pk):
                return field_name, serializer_field

        return None
    except AttributeError:
        return None


def get_serializer_pk_field_name(serializer) -> str | None:
    result = get_serializer_pk_field(serializer)

    if result is None:
        return None

    return result[0]
