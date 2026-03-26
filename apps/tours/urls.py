from rest_framework.routers import DefaultRouter
from .views import TourViewSet

router = DefaultRouter()
router.register('', TourViewSet, basename='tour')
urlpatterns = router.urls
