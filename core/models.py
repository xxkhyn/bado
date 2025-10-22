# models.py
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER  = "member", "一般"
        OFFICER = "officer", "運営"
        ADMIN   = "admin",   "管理者"
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["start"]
    def __str__(self):
        return self.title

class MagazineIssue(models.Model):
    title = models.CharField(max_length=200)
    issue_month = models.DateField(help_text="例: 2025-10-01")
    pdf = models.FileField(upload_to="magazines/")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-issue_month", "-created_at"]
    def __str__(self):
        return self.title

# 👇 参加している人だけ1行持つ
class EventAttendance(models.Model):
    event = models.ForeignKey('core.Event', on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_attendances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        indexes = [models.Index(fields=['event', 'user'])]

    def __str__(self):
        return f"{self.user} -> {self.event}"
