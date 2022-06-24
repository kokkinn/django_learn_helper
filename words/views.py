from django.shortcuts import render, redirect
from .models import Word
from django.http import HttpResponse
from .forms import WordForm


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


def create_word(request):
    form = WordForm()
    if request.method == "POST":
        form = WordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    context = {"form": form}
    return render(request, "words/word_form.html", context)


def update_word(request, uuid):
    word_object = Word.objects.get(id=uuid)
    form = WordForm(instance=word_object)
    if request.method == "POST":
        form = WordForm(request.POST, instance=word_object)
        if form.is_valid():
            form.save()
            return redirect("list_view")
    context = {"form": form}
    return render(request, "words/word_form.html", context)


def delete_view(request, uuid):
    word_object = Word.objects.get(id=uuid)
    if request.method == "POST":
        word_object.delete()
        return redirect("list_view")
    context = {"word": word_object}
    return render(request, "words/delete.html", context)
