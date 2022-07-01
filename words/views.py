from django import http
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from accounts.models import CustomUser
from .filters import WordFilter
from .models import Word, GroupOfWords
from django.http import HttpResponse
from .forms import WordForm, GroupForm, GroupFilterForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.edit import ProcessFormView, UpdateView, DeleteView, FormView

# from accounts.forms import AccountRegistrationForm, AccountUpdateForm, AccountProfileUpdate
from django.contrib import messages


class WordsListView(LoginRequiredMixin, ListView):
    context_object_name = "words"
    model = Word
    template_name = "words/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = WordFilter(self.request.GET, queryset=self.get_queryset())
        return context

    def get_queryset(self):
        super(WordsListView, self).get_queryset()
        return self.request.user.words.all()

    def get_template_names(self):
        super().get_template_names()
        if not self.request.user.words.all():
            return ["words/no_words.html"]
        else:
            return ["words/list.html"]

    def post(self, request):
        if "delete_button" in request.POST:
            checks = request.POST.getlist("checks")
            # print(checks)
            # print(request.POST)
            print(request.POST.getlist("csrfmiddlewaretoken"))
            for idi in checks:
                word = Word.objects.get(id=idi)
                word.delete()
            return redirect(reverse_lazy("words:list"))
        if "main_button" in request.POST:
            return redirect(reverse_lazy("words:home"))





class WordUpdateView(UpdateView, SingleObjectMixin):
    pk_url_kwarg = 'uuid'
    model = Word
    form_class = WordForm
    template_name = "words/word_form.html"
    success_url = reverse_lazy("words:list")


class WordCreateView(LoginRequiredMixin, CreateView):
    model = Word
    form_class = WordForm
    template_name = "words/word_form.html"
    success_url = reverse_lazy("words:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def home_view(request):
    return render(request, "words/home.html")


def one_word_view(request, uuid):
    word = Word.objects.get(id=uuid)
    context = {"word": word}
    return render(request, "words/single_word.html", context)


class GroupsListView(ListView):
    template_name = "words/groups_List.html"
    model = GroupOfWords
    context_object_name = 'groups'

    def post(self, request):
        checks = request.POST.getlist("checks[]")
        for idi in checks:
            group = GroupOfWords.objects.get(id=idi)
            group.delete()
        return redirect(reverse_lazy("words:groups_list"))


class GroupCreateView(FormView):
    model = GroupOfWords
    template_name = "words/group_form.html"
    form_class = GroupForm
    success_url = reverse_lazy("words:groups_list")

    def form_valid(self, form):
        super().form_valid(self)
        name = form.cleaned_data['name']
        words = form.cleaned_data['words']
        print(words)
        group = GroupOfWords(name=name)
        group.save()
        for word in words:
            group.words.add(word)
        return HttpResponseRedirect(reverse_lazy("words:groups_list"))


class GroupUpdateView(FormView):
    template_name = "words/group_form.html"
    form_class = GroupForm
    success_url = reverse_lazy("words:groups_list")
    pk_url_kwarg = "uuid"

    def get_initial(self):
        initial = super().get_initial()
        uuid = self.kwargs.get('uuid')
        group_obj = GroupOfWords.objects.get(id=uuid)
        initial['words'] = group_obj.words.all()
        initial["name"] = group_obj.name
        return initial

    def form_valid(self, form):
        super().form_valid(self)
        words = form.cleaned_data['words']
        uuid = self.kwargs.get('uuid')
        group_obj = GroupOfWords.objects.get(id=uuid)
        group_obj.words.clear()
        for word in words:
            group_obj.words.add(word)
        group_obj.save()
        return HttpResponseRedirect(reverse_lazy("words:groups_list"))


# def groups_list_view(request):
#     groups = GroupOfWords.objects.all()
#     context = {"groups": groups}
#     return render(request, "words/groups_list.html", context)


def words_in_group_list_view(request, uuid):
    words = GroupOfWords.objects.get(id=uuid).words.all()
    context = {"words": words}
    return render(request, "words/list.html", context)


def add_view(request):
    return render(request, "words/no_words.html")


def test_view(request):
    return render(request, "words/test.html")


# def create_word(request):
#     form = WordForm()
#     if request.method == "POST":
#         form = WordForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("index")
#     context = {"form": form}
#     return render(request, "words/word_form.html", context)


# def update_word(request, uuid):
#     word_object = Word.objects.get(id=uuid)
#     form = WordForm(instance=word_object)
#     if request.method == "POST":
#         form = WordForm(request.POST, instance=word_object)
#         if form.is_valid():
#             form.save()
#             return redirect("list_view")
#     context = {"form": form}
#     return render(request, "words/word_form.html", context)


def delete_view(request, uuid):
    word_object = Word.objects.get(id=uuid)
    if request.method == "POST":
        word_object.delete()
        return redirect(reverse_lazy("words:list"))
    context = {"word": word_object}
    return render(request, "words/delete.html", context)
