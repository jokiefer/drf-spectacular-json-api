from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.serializers import ModelSerializer, Serializer

from .models import Album, Song, User

__all__ = [
    "SongSerializer",
    "AlbumSerializer",
    "LoginSerializer",
    "UserSerializer"
]


class SongSerializer(ModelSerializer):
    """ """

    class Meta:
        model = Song
        fields = "__all__"


class AlbumSerializer(ModelSerializer):
    """ """

    songs = ResourceRelatedField(
        queryset=Song.objects,
        many=True,
        label=_("Songs"),
        help_text=_(
            "The songs which are part of this album."),
    )

    included_serializers = {
        "songs": SongSerializer
    }

    ordering_fields = ["id", "album", "title"]

    class Meta:
        model = Album
        fields = "__all__"


class PasswordField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class LoginSerializer(Serializer):
    """Simple non model serializer"""
    username = CharField(
        label=_("username"),
    )
    password = PasswordField(
        label=_("password"),
    )

    class Meta:
        resource_name = 'Login'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
