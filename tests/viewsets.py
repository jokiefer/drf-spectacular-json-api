from rest_framework_json_api.views import ModelViewSet

from tests.models import Album, Song
from tests.serializers import AlbumSerializer, SongSerializer


class AlbumViewset(ModelViewSet):

    serializer_class = AlbumSerializer
    queryset = Album.objects.none()


class SongViewset(ModelViewSet):

    serializer_class = SongSerializer
    queryset = Song.objects.none()
