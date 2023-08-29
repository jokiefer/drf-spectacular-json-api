from rest_framework_extensions.routers import ExtendedSimpleRouter

from .views import (AlbumModelViewset, NestedSongModelViewset,
                    SongModelViewset, UserModelViewset)

router = ExtendedSimpleRouter()


(
    router.register(r"albums", AlbumModelViewset, basename="album")
          .register(r"songs", NestedSongModelViewset, basename="album-songs", parents_query_lookups=["album"]),
    router.register(r"songs", SongModelViewset, basename="song"),
    router.register(r"users", UserModelViewset, basename="user"),
)

urlpatterns = router.urls
