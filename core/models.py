from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = "member", "一般"
        OFFICER = "officer", "運営"
        ADMIN   = "admin",   "管理者"
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

from django.db import models
from django.conf import settings

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 誰の予定か
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

