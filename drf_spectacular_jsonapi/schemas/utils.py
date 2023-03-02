from warnings import warn

from rest_framework.serializers import ModelSerializer


def get_primary_key_of_serializer(serializer) -> str | None:

    if issubclass(serializer.__class__, ModelSerializer):
        model = getattr(serializer.Meta, 'model')
        try:
            return next(field for field in serializer.fields.values() if field.source == model._meta.pk.name).field_name
        except StopIteration:
            pass
    warn(message="Can't resolve primary key for non model serializers.")
