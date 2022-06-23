from django.db import models
import uuid


class Word(models.Model):
    word1 = models.CharField(max_length=30)
    word2 = models.CharField(max_length=30)
    id = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True, editable=False, primary_key=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.word1} - {self.word2}"
