from django.http import Http404
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.settings import extensions_api_settings
from rest_framework_json_api.views import (AutoPrefetchMixin, ModelViewSet,
                                           PreloadIncludesMixin, RelatedMixin,
                                           RelationshipView)

from .models import Album, Song, User
from .serializers import (AlbumSerializer, SongPostOnlySerializer,
                          SongSerializer, UserSerializer)


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


class SongModelViewsetPostOnly(ModelViewSet):
    """ """
    serializer_class = SongPostOnlySerializer
    queryset = Song.objects.none()
    http_method_names = ["post"]


class UserModelViewset(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.none()


class NestedSongModelViewset(AutoPrefetchMixin, PreloadIncludesMixin, RelatedMixin, mixins.ListModelMixin,
                             GenericViewSet):
    """
    A viewset that provides default `list()` action for nested usage.
    """
    http_method_names = ["get", "head", "options"]
    serializer_class = SongSerializer
    queryset = Song.objects.none()

    def get_queryset(self):
        return self.filter_queryset_by_parents_lookups(
            super().get_queryset()
        )

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            try:
                return queryset.filter(**parents_query_dict)
            except ValueError:
                raise Http404
        else:
            return queryset

    def get_parents_query_dict(self):
        result = {}
        for kwarg_name, kwarg_value in self.kwargs.items():
            if kwarg_name.startswith(extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX):
                query_lookup = kwarg_name.replace(
                    extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX,
                    '',
                    1
                )
                query_value = kwarg_value
                result[query_lookup] = query_value
        return result


class AlbumRelationShipView(RelationshipView):
    queryset = Album.objects
