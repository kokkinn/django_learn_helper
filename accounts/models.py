from django.apps import apps
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True)
    avatar = models.ImageField(upload_to='profile/', default='default.png')
    birthday = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=0)

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.username


# @receiver(post_save, sender=Word)
# def custom_word(sender, instance, created, **kwargs):
#     apps.get_model("words.GroupOfWords").objects.create(name="General", user=instance)
#     print("User created")
