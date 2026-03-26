from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from utils.permissions import IsAdminOrReadOnly, IsAdmin
from .models import Blog, Category, Tag
from .serializers import BlogListSerializer, BlogDetailSerializer, CategorySerializer, TagSerializer


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['title', 'content', 'categories__name', 'tags__name']
    filterset_fields = ['is_published', 'categories__slug', 'tags__slug', 'author']
    ordering_fields = ['published_at', 'created_at']

    def get_queryset(self):
        qs = Blog.objects.select_related('author').prefetch_related('categories', 'tags')
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return qs
        return qs.filter(is_published=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogListSerializer
        return BlogDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
