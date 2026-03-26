from django.db import models
from apps.destinations.models import Destination


class Tour(models.Model):
    CURRENCY_CHOICES = [('BDT', 'Taka'), ('USD', 'US Dollar'), ('EUR', 'Euro')]

    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name='tours')
    title = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    description = models.TextField()
    duration_days = models.PositiveIntegerField(default=1)
    duration_hours = models.PositiveIntegerField(default=0)
    max_group_size = models.PositiveIntegerField(default=15)
    languages = models.CharField(max_length=200, default='English, Bangla')
    highlights = models.JSONField(default=list)
    included = models.JSONField(default=list)
    excluded = models.JSONField(default=list)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BDT')
    price_adult = models.DecimalField(max_digits=10, decimal_places=2)
    price_child = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_infant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    thumbnail = models.ImageField(upload_to='tours/thumbnails/')
    booking_cutoff_days = models.PositiveIntegerField(default=1, help_text='Hide availability within this many days from today')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tours'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['destination', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Tour.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'tour_images'
        ordering = ['order']


class Itinerary(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary')
    day = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='tours/itinerary/', null=True, blank=True)

    class Meta:
        db_table = 'tour_itinerary'
        ordering = ['day']
        unique_together = ['tour', 'day']


class CancellationPolicy(models.Model):
    tour = models.OneToOneField(Tour, on_delete=models.CASCADE, related_name='cancellation_policy')
    free_cancellation_hours = models.PositiveIntegerField(default=24, help_text='Hours before tour start for free cancellation')
    partial_refund_percent = models.PositiveIntegerField(default=50)
    partial_refund_hours = models.PositiveIntegerField(default=12, help_text='Hours before tour start for partial refund')
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'cancellation_policies'
