from django.db import models


class Destination(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    country = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='destinations/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'destinations'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
