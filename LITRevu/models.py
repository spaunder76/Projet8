from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ticket_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    time_created = models.DateTimeField(default=timezone.now)

class UserFollows(models.Model):
    user = models.ForeignKey(to=User, related_name='following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(to=User, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'followed_user')
