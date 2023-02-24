from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import AlbumModelViewset, LoginRequestView, SongModelViewset

router = SimpleRouter()


(
    router.register("albums", AlbumModelViewset),
    router.register("songs", SongModelViewset)
)

urlpatterns = router.urls
urlpatterns.extend([
    path('login/', LoginRequestView.as_view(), name='login'),
])
