import random

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
from .forms import WordForm, GroupForm, GroupFilterForm, GroupChoiceForm, TestInputForm
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

    def get_queryset(self):
        super(WordsListView, self).get_queryset()
        return self.request.user.words.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = WordFilter(self.request.GET, queryset=self.get_queryset(), request=self.request)
        return context

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
        form.instance.save()
        general_group = GroupOfWords.objects.get(user=self.request.user, name="General")
        general_group.words.add(form.instance)
        general_group.save()
        # print(self.request.user.groups_of_words)
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

    def get_queryset(self):
        super(GroupsListView, self).get_queryset()
        return self.request.user.groups_of_words.all()

    def post(self, request):
        checks = request.POST.getlist("checks[]")
        for idi in checks:
            group = GroupOfWords.objects.get(id=idi)
            if group.name == "General":
                return HttpResponseRedirect(reverse_lazy("words:home"))
            group.delete()
        return redirect(reverse_lazy("words:groups_list"))


class GroupCreateView(FormView):
    model = GroupOfWords
    template_name = "words/group_form.html"
    form_class = GroupForm
    success_url = reverse_lazy("words:groups_list")

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""
        kwargs = super(GroupCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        super().form_valid(self)
        group_obj = form.instance
        words = form.cleaned_data['words']
        group_obj.user = self.request.user
        group_obj.save()
        for word in words:
            group_obj.words.add(word)
        group_obj.save()

        return HttpResponseRedirect(reverse_lazy("words:groups_list"))


class GroupUpdateView(FormView):
    template_name = "words/group_form.html"
    form_class = GroupForm
    success_url = reverse_lazy("words:groups_list")
    pk_url_kwarg = "uuid"

    def get(self, request, *args, **kwargs):
        uuid = self.kwargs.get('uuid')
        group_obj = GroupOfWords.objects.get(id=uuid)
        if group_obj.name == "General":
            return HttpResponseRedirect(reverse_lazy("words:home"))
        return super().get(self, request, *args, **kwargs)

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""
        kwargs = super(GroupUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

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


class WordsInGroupListView(ListView):
    model = Word
    context_object_name = "words"
    pk_url_kwarg = 'uuid'

    def get_queryset(self):
        super(WordsInGroupListView, self).get_queryset()
        uuid = self.kwargs.get("uuid")
        return GroupOfWords.objects.get(id=uuid).words.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs.get("uuid")
        context["group_obj"] = GroupOfWords.objects.get(id=uuid)
        return context

    def get_template_names(self):
        super().get_template_names()
        if not self.request.user.words.all():
            return ["words/no_words.html"]
        else:
            return ["words/words_in_group_list.html"]

    # def post(self, request):
    #     if "delete_button" in request.POST:
    #         checks = request.POST.getlist("checks")
    #         # print(checks)
    #         # print(request.POST)
    #         print(request.POST.getlist("csrfmiddlewaretoken"))
    #         for idi in checks:
    #             word = Word.objects.get(id=idi)
    #             word.delete()
    #         return redirect(reverse_lazy("words:list"))
    #     if "main_button" in request.POST:
    #         return redirect(reverse_lazy("words:home"))


# class WordsInGroupListView(ListView)

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


class TestsHomeView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(TestsHomeView, self).get_context_data(**kwargs)
        context["form"] = GroupChoiceForm(self.request.user)
        return context

    def post(self, request):
        # a = self.request.POST.getlist("group")[0]
        a = self.request.POST
        print(f"\nPost request from tests home view: {a}\n")
        kwargs = {'uuid': self.request.POST.getlist("groups")[0]}
        # print(kwargs)
        return redirect(
            reverse_lazy("words:groups_of_words_test", kwargs=kwargs))
        # return redirect(f"tests/groups_of_words_test/{self.request.POST.getlist('groups')[0]}")

    template_name = "tests/tests_home.html"


class QuickTest(View):
    template_name = "tests/quick_test.html"

    def __init__(self):
        super().__init__()
        # self.word_obj = Word.objects.order_by("score").first()
        self.word_obj = random.choice(Word.objects.all())

    def get(self, request):
        print("From quictest GET", self.word_obj)
        context = {"word": self.word_obj}
        return render(request=request, template_name=self.template_name, context=context)

    def post(self, request):
        print("From quictest POST", self.word_obj)
        if self.word_obj.word2 == self.request.POST.getlist("input_text")[0]:
            a = Word.objects.get(id=self.word_obj.id)
            a.score += 1
            a.save()
        else:
            a = Word.objects.get(id=self.word_obj.id)
            a.score -= 1
            a.save()
        print(self.request.POST.getlist("input_text")[0])

        return redirect(reverse_lazy("words:quick_test"))


class GroupOfWordsTest(FormView):
    pk_url_kwarg = "uuid"
    template_name = "tests/quick_test.html"
    form_class = TestInputForm
    model = Word

    # def __init__(self):
    #     super().__init__()
    #     self.group_obj = None
    #     self.word_obj = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs.get("uuid")
        context["group_obj"] = GroupOfWords.objects.get(id=uuid)
        context["word_obj"] = random.choice(context["group_obj"].words.all())
        return context

    # def get_object(self):
    #     uuid = self.kwargs.get("uuid")
    #     self.group_obj = GroupOfWords.objects.get(id=uuid)
    #     self.word_obj = random.choice(self.group_obj.words.all())
    #
    # def get(self, request, *args, **kwargs):
    #     self.get_object()
    #     print(self.request.GET)
    #     print("FROM GET", self.word_obj)
    #     # super().get(self, request, *args, **kwargs)
    #     context = {"word": self.word_obj, "group_obj": self.group_obj}
    #     return render(request=request, template_name=self.template_name, context=context)
    #

    def form_valid(self, form):
        print(f"\nFORM INSTANCE FROM form_valid : {form.instance} \n")
        print(f"\nC.D. FROM form_valid: {self.get_context_data()} \n")
        return super().form_valid(form)
    # def post(self, request, **kwargs):
    #     print("POST", request.POST)

    # print("AAA", self.word_obj)
    # print("A WORD", self.word_obj.score, self.word_obj.word1, self.word_obj.word2)
    # print("INPUT", self.request.POST.getlist("input_text")[0])
    # if self.word_obj.word2 == self.request.POST.getlist("input_text")[0]:
    #     self.word_obj.score += 1
    #     print(self.word_obj.score, "\n")
    # else:
    #     self.word_obj.score -= 1
    #     print(self.word_obj.score, "\n")
    # self.word_obj.save()
    # return redirect(reverse_lazy(f"words:groups_of_words_test", kwargs={'uuid': self.get_object()[1].id}))
