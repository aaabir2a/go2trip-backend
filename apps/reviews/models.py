from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.authentication.models import User
from apps.tours.models import Tour


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'tour']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.tour.title} ({self.rating}★)'
