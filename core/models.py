import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


def validate_egyptian_phone(value):
    if not re.match(r'^01[0-25]{1}[0-9]{8}$', value):
        raise ValidationError(f'{value} is not a valid Egyptian phone number')


class User(AbstractUser):
    mobile_phone = models.CharField(max_length=11, unique=True, validators=[validate_egyptian_phone])

    def __str__(self):
        return self.email


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    details = models.TextField()
    total_target = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
