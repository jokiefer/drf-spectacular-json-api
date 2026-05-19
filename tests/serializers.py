from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as drf_serializers
from rest_framework.fields import CharField
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import ModelSerializer

from .models import Album, Song, User

__all__ = [
    "SongSerializer",
    "AlbumSerializer",
    "AlbumWithEmbeddedSerializer",
    "EmbeddedDimensionsSerializer",
    "UserSerializer",
]


class SongSerializer(ModelSerializer):
    """ """
    created_by = ResourceRelatedField(
        model=User,
        label=_("Created By"),
        help_text=_(
            "The user which created this song"),
        required=False,
        read_only=True,
    )

    class Meta:
        model = Song
        fields = "__all__"


class SongPostOnlySerializer(SongSerializer):
    pass


class EmbeddedDimensionsSerializer(drf_serializers.Serializer):
    """Plain JSON object nested under JSON:API ``attributes`` (not a resource)."""

    width = drf_serializers.IntegerField()
    height = drf_serializers.IntegerField()


class AlbumSerializer(ModelSerializer):
    """ """

    songs = ResourceRelatedField(
        queryset=Song.objects,
        many=True,
        label=_("Nice Songs"),
        help_text=_(
            "The songs which are part of this album."),
        required=False
    )

    included_serializers = {
        "songs": SongSerializer
    }

    ordering_fields = ["id", "album", "title"]

    class Meta:
        model = Album
        fields = "__all__"


class AlbumWithEmbeddedSerializer(AlbumSerializer):
    """Album JSON:API resource with a nested non-resource object attribute."""

    dimensions = EmbeddedDimensionsSerializer(required=False)

    class Meta(AlbumSerializer.Meta):
        fields = ("id", "title", "genre", "year", "released", "songs", "dimensions")


class PasswordField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
