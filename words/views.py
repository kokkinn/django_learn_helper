from django.shortcuts import render
from .models import Word
from django.http import HttpResponse


def home_view(request):
    return render(request, "words/home.html")


def one_word_view(request, uuid):
    word = Word.objects.get(id=uuid)
    context = {"word": word}
    return render(request, "words/single_word.html", context)


def list_view(request):
    words = Word.objects.all()
    context = {"words": words}
    return render(request, "words/list.html", context)


def add_view(request):
    return render(request, "words/add.html")


def test_view(request):
    return render(request, "words/test.html")
