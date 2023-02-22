from rest_framework_json_api.serializers import ModelSerializer

from .models import Album, Song

__all__ = [
    "SongSerializer",
    "AlbumSerializer"
]


class SongSerializer(ModelSerializer):
    """ """

    class Meta:
        model = Song
        fields = "__all__"


class AlbumSerializer(ModelSerializer):
    """ """

    songs = SongSerializer(many=True, read_only=True)
    single = SongSerializer(read_only=True)

    included_serializers = {
        "songs": SongSerializer
    }

    ordering_fields = ["id", "album", "title"]

    class Meta:
        model = Album
        fields = "__all__"
