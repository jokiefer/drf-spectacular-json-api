from rest_framework_json_api.views import ModelViewSet

from .models import Album, Song, User
from .serializers import AlbumSerializer, SongSerializer, UserSerializer


class AlbumModelViewset(ModelViewSet):
    """ """
    serializer_class = AlbumSerializer
    queryset = Album.objects.none()
    search_fields = ("id", "songs",)
    ordering_fields = ["id", "title"]
    filterset_fields = {
        "genre": ["exact"],
        "title": ["contains"]
    }


class SongModelViewset(ModelViewSet):
    """ """
    serializer_class = SongSerializer
    queryset = Song.objects.none()


class UserModelViewset(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.none()
