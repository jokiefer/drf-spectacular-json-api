from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as drf_serializers
from rest_framework.fields import CharField
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import ModelSerializer

from .models import Album, Song, SpecialSong, User

__all__ = [
    "SongSerializer",
    "AlbumSerializer",
    "AlbumWithEmbeddedSerializer",
    "EmbeddedDimensionsSerializer",
    "UserSerializer",
    "UserWithSongsSerializer",
    "SongWithCreatorSerializer",
    "AlbumWithNestedIncludesSerializer",
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


class SpecialSongSerializer(ModelSerializer):
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
        model = SpecialSong
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
        fields = ("id", "title", "genre", "year",
                  "released", "songs", "dimensions")


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


class SongWithCreatorSerializer(SongSerializer):
    """Song which can be narrowed down to its creator, and that creator to his songs.

    The two serializers point at each other on purpose: ``song -> created_by ->
    singles -> song`` is the ordinary shape of a json:api graph, and a schema
    generator must not walk in circles over it. Both entries are written the way the
    library allows them to be written, once as a class and once as a dotted path.
    """

    included_serializers = {
        "created_by": "tests.serializers.UserWithSongsSerializer"
    }


class UserWithSongsSerializer(UserSerializer):
    """User whose own songs are includeable through the reverse relation."""

    included_serializers = {
        "singles": SongWithCreatorSerializer
    }


class AlbumWithNestedIncludesSerializer(AlbumSerializer):
    """Album whose songs are includeable and whose songs' creators are too.

    ``User`` is only reachable through the nested include path
    ``songs.created_by``, which is where an included resource stops being one level
    away from the endpoint.
    """

    included_serializers = {
        "songs": SongWithCreatorSerializer
    }
