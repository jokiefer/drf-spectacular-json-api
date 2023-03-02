from rest_framework.routers import SimpleRouter

from .views import AlbumModelViewset, SongModelViewset, UserModelViewset

router = SimpleRouter()


(
    router.register("albums", AlbumModelViewset),
    router.register("songs", SongModelViewset),
    router.register("users", UserModelViewset),
)

urlpatterns = router.urls
