from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TourAvailabilityView, ScheduleManageViewSet

router = DefaultRouter()
router.register('schedules', ScheduleManageViewSet, basename='schedule')

urlpatterns = router.urls + [
    path('<slug:slug>/', TourAvailabilityView.as_view(), name='tour-availability'),
]
