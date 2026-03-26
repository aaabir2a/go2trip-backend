from rest_framework.routers import DefaultRouter
from .views import BlogViewSet, CategoryViewSet, TagViewSet

router = DefaultRouter()
router.register('', BlogViewSet, basename='blog')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')
urlpatterns = router.urls
