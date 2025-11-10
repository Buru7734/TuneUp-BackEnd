from django.db import models
from django.conf import settings
from django.db.models import Avg, Count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_given")
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_received")
    gig = models.ForeignKey('gigs.Gig', on_delete=models.CASCADE, related_name="reviews") 
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("reviewer", "reviewed_user", "gig")
        
    def __str__(self):
        return f"{self.reviewer.username} - {self.reviewed_user.username}: {self.rating}"
    
def update_user_rating(user):
    from accounts.models import CustomUser
    from .models import Review
    
    reviews = Review.objects.filter(reviewed_user=user)
    stats = reviews.aggregate(avg=Avg('rating'), total=Count('id'))
    user.rating = round(stats['avg'] or 0,2)
    user.total_reviews = stats['total']
    user.save(update_fields=['rating', 'total_reviews'])
    
@receiver(post_save, sender=Review)
def update_rating_on_save(sender, instance, **kwargs):
    update_user_rating(instance.reviewed_user)
    
@receiver(post_delete, sender=Review)
def update_rating_on_delete(sender, instance, **kwargs):
    update_user_rating(instance.reviewed_user)