from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import Blog, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class BlogListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'thumbnail', 'author_name', 'categories', 'tags', 'is_published', 'published_at', 'created_at']


class BlogDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False, source='tags'
    )

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'content', 'thumbnail', 'author', 'categories', 'tags',
                  'category_ids', 'tag_ids', 'is_published', 'published_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'author', 'published_at', 'created_at', 'updated_at']
