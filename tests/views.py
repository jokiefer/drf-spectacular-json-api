from rest_framework_json_api.views import ModelViewSet

from .models import Album, Song
from .serializers import AlbumSerializer, SongSerializer


class AlbumModelViewset(ModelViewSet):
    """ """
    serializer_class = AlbumSerializer
    queryset = Album.objects.none()
    search_fields = ("id", "songs",)
    ordering_fields = ["id", "title"]


class SongModelViewset(ModelViewSet):
    """ """
    serializer_class = SongSerializer
    queryset = Song.objects.none()
