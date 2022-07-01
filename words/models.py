from django.db import models
import uuid

from accounts.models import CustomUser

import random

from faker import Faker


class GroupOfWords(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)

    def __str__(self):
        return self.name


class Word(models.Model):
    user = models.ForeignKey(to=CustomUser, related_name="words", on_delete=models.CASCADE)
    word1 = models.CharField(max_length=30)
    word2 = models.CharField(max_length=30)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    score = models.IntegerField(default=0)
    # group = models.ForeignKey(GroupOfWords, null=True, blank=True, related_name="words", default=1,
    #                           on_delete=models.SET_NULL)
    group = models.ManyToManyField(to=GroupOfWords, related_name='words', null=True, blank=True)

    def __str__(self):
        return f"{self.word1} - {self.word2}"

    def save(self, *args, **kwargs):
        print("FUCK YOU!!!!!!")
        super().save(*args, **kwargs)

    @classmethod
    def generate(cls):
        faker = Faker()
        for _ in range(1, 30):
            wordobj = Word(word1=f"{faker.word()}", word2=f"{faker.word()}")
            wordobj.user = random.choice(list(CustomUser.objects.all()))
            wordobj.save()
            wordobj.group.add(random.choice(list(GroupOfWords.objects.all())))
