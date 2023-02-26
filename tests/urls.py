from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (AlbumModelViewset, LoginRequestView, SongModelViewset,
                    UserModelViewset)

router = SimpleRouter()


(
    router.register("albums", AlbumModelViewset),
    router.register("songs", SongModelViewset),
    router.register("users", UserModelViewset),
)

urlpatterns = router.urls
urlpatterns.extend([
    path('login/', LoginRequestView.as_view(), name='login'),
])
