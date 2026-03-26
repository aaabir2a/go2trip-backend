from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.permissions import IsAdmin
from utils.responses import success_response, created_response
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    filterset_fields = ['tour', 'rating', 'is_approved']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action in ['approve', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        if self.request.method == 'GET':
            return Review.objects.filter(is_approved=True).select_related('user', 'tour')
        if user.is_authenticated and user.role == 'admin':
            return Review.objects.select_related('user', 'tour')
        return Review.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return created_response(data=ReviewSerializer(review).data, message='Review submitted. Pending approval.')

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = not review.is_approved
        review.save()
        state = 'approved' if review.is_approved else 'unapproved'
        return success_response(message=f'Review {state}.')
