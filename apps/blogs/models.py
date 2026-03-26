from django.db import models
from apps.authentication.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        db_table = 'blog_categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        db_table = 'blog_tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='blogs')
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to='blogs/thumbnails/')
    categories = models.ManyToManyField(Category, related_name='blogs', blank=True)
    tags = models.ManyToManyField(Tag, related_name='blogs', blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blogs'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_published', '-published_at'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
