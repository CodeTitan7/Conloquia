import uuid
from django.db import models
from django.utils import timezone

class Email(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    category = models.CharField(max_length=20, choices=[
        ('inbox', 'Inbox'),
        ('sent', 'Sent'),
        ('draft', 'Draft'),
        ('trash', 'Trash'),
    ],
        default='inbox')
    sent_at = models.DateTimeField(null=True, blank=True)
    starred = models.BooleanField(default=False)  # New field for star functionality

    class Meta:
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return self.subject

class EmailTracking(models.Model):
    email = models.OneToOneField(Email, on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Tracking for {self.email.subject}"
