from django.db import models
import uuid


class GroupOfWords(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)

    def __str__(self):
        return self.name


class Word(models.Model):
    word1 = models.CharField(max_length=30)
    word2 = models.CharField(max_length=30)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    score = models.IntegerField(default=0)
    # group = models.ForeignKey(GroupOfWords, null=True, blank=True, related_name="words", default=1,
    #                           on_delete=models.SET_NULL)
    group = models.ManyToManyField(to=GroupOfWords, related_name='words')

    def __str__(self):
        return f"{self.word1} - {self.word2}"
