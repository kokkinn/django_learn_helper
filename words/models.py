import googletrans
from django.db import models
import uuid
from googletrans import Translator, constants
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser

import random

from faker import Faker


class GroupOfWords(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(to=CustomUser, related_name="groups_of_words", on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name


class Word(models.Model):
    user = models.ForeignKey(to=CustomUser, related_name="words", on_delete=models.CASCADE)
    word1 = models.CharField(max_length=30, unique=True)
    word2 = models.CharField(max_length=30)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    score = models.IntegerField(default=0)
    group = models.ManyToManyField(to=GroupOfWords, related_name='words', blank=True, null=True)

    #
    # def __str__(self):
    #     return f"{self.word1}: {self.word2}, {self.score}, {str(self.id)[0:4]}"

    # def save(self, *args, **kwargs):
    #
    #     print("'Word' instance created")
    #     super().save(*args, **kwargs)

    @classmethod
    def generate(cls, num):
        faker = Faker()
        for _ in range(1, num):
            translator = Translator()
            word1 = faker.word()
            tr = translator.translate(str(word1), src="en", dest="ru")
            word2 = tr.text
            wordobj = Word(word1=f"{word1}", word2=f"{word2}")
            wordobj.user = CustomUser.objects.get(username="admin")
            wordobj.score = random.randint(-10, 50)
            wordobj.save()
            # wordobj.group.add(random.choice(list(wordobj.user.groups_of_words.all())))
            wordobj.group.add(wordobj.user.groups_of_words.get(name="General"))
            wordobj.save()


@receiver(post_save, sender=Word)
def custom_word(sender, instance, created, **kwargs):
    if created:
        # print(kwargs)
        # general_group = GroupOfWords.objects.get(user=kwargs.request.user, name="General")
        # general_group.words.add(instance)
        # kw
        # general_group.save()
        print(f"Word instance created: '{instance}'")


class Result(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    details = models.JSONField(default=dict)
    ended = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
