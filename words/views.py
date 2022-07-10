import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .filters import WordFilter
from .models import Word, GroupOfWords

from .forms import WordForm, GroupForm, GroupFilterForm, GroupChoiceForm, TestInputForm, TestParametersForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.edit import ProcessFormView, UpdateView, DeleteView, FormView


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

        words_qs = Word.objects.all()
        total_score = 0
        for word in words_qs:
            total_score += word.score
        context["min"] = words_qs.order_by("score").first().score
        context["max"] = words_qs.order_by("score").last().score
        context["avg"] = round(total_score / words_qs.count(), 2)

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
        initial["description"] = group_obj.description
        return initial

    def form_valid(self, form):
        super().form_valid(self)
        words = form.cleaned_data['words']
        uuid = self.kwargs.get('uuid')
        group_obj = GroupOfWords.objects.get(id=uuid)
        group_obj.words.clear()
        for word in words:
            group_obj.words.add(word)
        group_obj.description = form.cleaned_data["description"]
        group_obj.name = form.cleaned_data["name"]
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
    template_name = "tests/tests_home.html"

    def get_context_data(self, **kwargs):
        try:
            del self.request.session['list_test_words']
            del self.request.session['test_eval']
        except KeyError:
            pass
        context = super(TestsHomeView, self).get_context_data(**kwargs)
        context["form"] = TestParametersForm(self.request.user)
        return context

    def post(self, request):
        print("\n------------POST VIEW START-----------")
        uuid = self.request.POST.getlist("groups")[0]
        kwargs = {'uuid': uuid}

        if request.POST.getlist("durations")[0] == "finite":
            request.session['is_finite'] = True
            words_qs = GroupOfWords.objects.get(id=uuid).words.all()
            list_test_words = [str(word.id) for word in words_qs]
            request.session['list_test_words'] = list_test_words
            print(request.session['list_test_words'])
        elif request.POST.getlist("durations")[0] == "loop":
            request.session['is_finite'] = False

        if request.POST.getlist("type")[0] == "ranked":
            request.session["test_eval"] = "ranked"
        elif request.POST.getlist("type")[0] == "unranked":
            request.session["test_eval"] = "unranked"

        print("\n------------POST VIEW END-----------")
        return redirect(
            reverse_lazy("words:groups_of_words_test", kwargs=kwargs))


class GroupOfWordsTest(FormView):
    pk_url_kwarg = "uuid"
    template_name = "tests/quick_test.html"
    form_class = TestInputForm
    model = Word
    success_url = reverse_lazy("words:list")

    def get(self, request, *args, **kwargs):
        if not request.session['list_test_words']:
            del request.session['list_test_words']
            return redirect(reverse_lazy("words:tests_home"))
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print("\n-----------------------------------START-----------------------------------------")

        context = super().get_context_data(**kwargs)
        if self.request.session["is_finite"]:
            uuid = self.kwargs.get("uuid")
            # self.request.session["kakaka"] = 123456
            context["group_obj"] = GroupOfWords.objects.get(id=uuid)
            # print(f"\nCONTEXT DATA from get_context_data: {context}\n")
            # qs = serializers.serialize('json', qs)
            randint = random.randint(0, len(self.request.session["list_test_words"]) - 1)
            print(self.request.session["list_test_words"])
            a = self.request.session["list_test_words"].pop(randint)
            self.request.session["pupa"] = 1
            print(self.request.session["list_test_words"])
            # self.request.session["list_test_words"].pop(randint)
            # print(self.request.session["list_test_words"])
            print("Session key updated")
            print(a)
            context["word_obj"] = Word.objects.get(id=a)
            return context
        else:
            uuid = self.kwargs.get("uuid")
            context["group_obj"] = GroupOfWords.objects.get(id=uuid)
            context["word_obj"] = random.choice(context["group_obj"].words.all())
            print(f"\nCONTEXT DATA from get_context_data: {context}\n")
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
        if form.is_valid():
            print(f"\nFORM INSTANCE from form_valid : {form.instance}")
            print(f"\nREQUEST from form_valid: {self.request.POST}\n")

            print(f"{self.request.session['list_test_words']}\n")
            print(f"{self.request.session['pupa']}\n")
            uuid = self.request.POST.getlist("word_obj")[0]
            word_obj = Word.objects.get(id=uuid)
            input_word = self.request.POST.getlist("word1")[0]
            print("Word was", word_obj)
            print("Input word", input_word)
            if word_obj.word2 == input_word:
                word_obj.score += 1
                print("foo", word_obj.score, "\n")
            else:
                word_obj.score -= 1
                print("foooooo", word_obj.score, "\n")
            word_obj.save()
            print("------------------------------------END----------------------------------------\n")
            return redirect(
                reverse_lazy(f"words:groups_of_words_test", kwargs={'uuid': self.kwargs["uuid"]}))

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
