from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    # avatar = models.ImageField(null=True, blank=True, default="default.png", upload_to="avatars/")

    def __str__(self):
        return ""
