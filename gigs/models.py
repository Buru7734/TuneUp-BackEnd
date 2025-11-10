from django.db import models
from django.conf import settings
from accounts.models import CustomUser

# Create your models here.


    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags_created",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

class Gig(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="organized_gigs"
    )
    
    musicians = models.ManyToManyField(
        CustomUser,
        related_name="joined_gigs",
        blank=True
    )
    
    tags = models.ManyToManyField(
        Tag,
        related_name="gigs",
        blank=True
    )
    
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.organizer.username}"

class GigApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected','Rejected') 
    ]
    
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    gig = models.ForeignKey('Gig', on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'gig')
    
    def __str__(self):
        return f"{self.applicant.username} → {self.gig.title} ({self.status})"