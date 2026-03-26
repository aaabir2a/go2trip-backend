from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsAdminOrReadOnly, IsAdmin
from utils.responses import success_response, created_response
from .models import Tour, TourImage, Itinerary, CancellationPolicy
from .serializers import TourListSerializer, TourDetailSerializer, TourImageSerializer, ItinerarySerializer, CancellationPolicySerializer
from .filters import TourFilter


class TourViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filterset_class = TourFilter
    search_fields = ['title', 'description', 'destination__name']
    ordering_fields = ['price_adult', 'created_at', 'duration_days']

    def get_queryset(self):
        qs = Tour.objects.select_related('destination').prefetch_related('images', 'reviews')
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return qs
        return qs.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return TourListSerializer
        return TourDetailSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAdmin])
    def images(self, request, slug=None):
        tour = self.get_object()
        if request.method == 'POST':
            serializer = TourImageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(tour=tour)
            return created_response(data=serializer.data, message='Image uploaded.')
        image_id = request.data.get('image_id')
        TourImage.objects.filter(id=image_id, tour=tour).delete()
        return success_response(message='Image deleted.')

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def itinerary(self, request, slug=None):
        tour = self.get_object()
        serializer = ItinerarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tour=tour)
        return created_response(data=serializer.data, message='Itinerary item added.')

    @action(detail=True, methods=['post', 'put'], permission_classes=[IsAdmin], url_path='cancellation-policy')
    def cancellation_policy(self, request, slug=None):
        tour = self.get_object()
        policy, _ = CancellationPolicy.objects.get_or_create(tour=tour)
        serializer = CancellationPolicySerializer(policy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message='Policy updated.')
