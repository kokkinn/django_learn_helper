import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.detail import SingleObjectMixin, DetailView

from words.filters import WordFilter
from words.models import Word, GroupOfWords, Result

from words.forms import WordForm, GroupForm, GroupFilterForm, GroupChoiceForm, TestInputForm, TestParametersForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic.edit import ProcessFormView, UpdateView, DeleteView, FormView


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


def add_view(request):
    return render(request, "words/no_words.html")


def test_view(request):
    return render(request, "words/test.html")
