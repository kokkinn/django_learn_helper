from django.shortcuts import render, redirect
from .models import Word, GroupOfWords
from django.http import HttpResponse
from .forms import WordForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView
from django.views.generic.edit import ProcessFormView

from accounts.forms import AccountRegistrationForm, AccountUpdateForm, AccountProfileUpdate
from django.contrib import messages


class WordsListView(ListView):
    context_object_name = "words"
    model = Word
    template_name = "words/list.html"


# def total_list_view(request):
#     words = Word.objects.all()
#     context = {"words": words}
#     return render(request, "words/list.html", context)


def home_view(request):
    return render(request, "words/home.html")


def one_word_view(request, uuid):
    word = Word.objects.get(id=uuid)
    context = {"word": word}
    return render(request, "words/single_word.html", context)


def groups_list_view(request):
    groups = GroupOfWords.objects.all()
    context = {"groups": groups}
    return render(request, "words/groups_list.html", context)


def words_in_group_list_view(request, uuid):
    words = GroupOfWords.objects.get(id=uuid).words.all()
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
