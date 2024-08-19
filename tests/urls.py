from django.urls import path
from rest_framework_extensions.routers import ExtendedSimpleRouter

from .views import (AlbumModelViewset, AlbumRelationShipView,
                    NestedSongModelViewset, SongModelViewset,
                    SongModelViewsetPostOnly, UserModelViewset)

router = ExtendedSimpleRouter()


(
    router.register(r"albums", AlbumModelViewset, basename="album")
          .register(r"songs", NestedSongModelViewset, basename="album-songs", parents_query_lookups=["album"]),
    router.register(r"songs", SongModelViewset, basename="song"),
    router.register(r"songs-post-only",
                    SongModelViewsetPostOnly, basename="song-post"),

    router.register(r"users", UserModelViewset, basename="user"),
)


urlpatterns = [
    path(r"albums/{parent_lookup_album}/songs-as-view/",
         NestedSongModelViewset.as_view({"get": "list"})
         ),
    path(
        r'^albums/(?P<pk>[^/.]+)/relationships/(?P<related_field>[-/w]+)$',
        AlbumRelationShipView.as_view(),
        name='order-relationships'
    )
]


urlpatterns += router.urls
