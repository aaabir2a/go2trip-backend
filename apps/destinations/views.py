from rest_framework import viewsets
from utils.permissions import IsAdminOrReadOnly
from .models import Destination
from .serializers import DestinationSerializer


class DestinationViewSet(viewsets.ModelViewSet):
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['name', 'country', 'location']
    filterset_fields = ['country']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        qs = Destination.objects.all()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin':
            return qs
        return qs.filter(is_active=True)
