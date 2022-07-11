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

import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView

from words.models import Word, GroupOfWords, Result

from words.forms import TestInputForm, TestParametersForm

from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView


def create_result_json(list_of_uuids):
    json = {"test_words": {}}
    for uuid in list_of_uuids:
        json["test_words"][f"{uuid}"] = {"input_word": None, "is_correct": None}
    return json


class TestsHomeView(TemplateView):
    template_name = "tests/tests_home.html"

    def get_context_data(self, **kwargs):
        # tuple_sessions_keys_to_delete = ("result_id", "is_finite", 'list_test_words', 'test_eval')
        # for key in tuple_sessions_keys_to_delete:
        #     try:
        #         del self.request.session[f"{key}"]
        #     except KeyError:
        #         pass
        context = super(TestsHomeView, self).get_context_data(**kwargs)
        context["form"] = TestParametersForm(self.request.user)
        return context

    def post(self, request):
        print("\n------------POST VIEW START-----------")
        uuid = self.request.POST.getlist("groups")[0]
        kwargs = {'uuid': uuid}
        request.session['test_params'] = {}

        if request.POST.getlist("durations")[0] == "finite":
            request.session['test_params']["duration"] = "finite"
            words_qs = GroupOfWords.objects.get(id=uuid).words.all()
            list_test_words = [str(word.id) for word in words_qs]
            request.session['test_params']["list_test_words"] = list_test_words
            result = Result.objects.create(user=request.user, details=create_result_json(list_test_words))
            result.save()
            request.session["test_params"]["result_id"] = str(result.id)
        elif request.POST.getlist("durations")[0] == "loop":
            request.session['test_params']['duration'] = "loop"

        if request.POST.getlist("type")[0] == "ranked":
            request.session['test_params']["test_eval"] = "ranked"
        elif request.POST.getlist("type")[0] == "unranked":
            request.session['test_params']["test_eval"] = "unranked"

        if request.POST.getlist("test_for_translation_of")[0] == "for_w1":
            request.session["test_params"]["for_wX"] = 1
        elif request.POST.getlist("test_for_translation_of")[0] == "for_w2":
            request.session["test_params"]["for_wX"] = 2

        request.session['test_params']["is_ended"] = False
        request.session.modified = True
        print("\n------------POST VIEW END-----------")
        return redirect(
            reverse_lazy("words:groups_of_words_test", kwargs=kwargs))


class GroupOfWordsTest(FormView):
    pk_url_kwarg = "uuid"
    template_name = "tests/quick_test.html"
    form_class = TestInputForm
    model = Word
    success_url = reverse_lazy("words:list")

    def __init__(self, **kwargs):
        # print("\n", kwargs["result"], "\n")
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        if not request.session["test_params"]:
            return redirect(reverse_lazy("words:tests_home"))
        try:
            if not request.session["test_params"]['list_test_words']:
                del request.session["test_params"]
                return redirect(reverse_lazy("words:tests_home"))
        except KeyError:
            pass
        return self.render_to_response(self.get_context_data(req=request))
        # return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        request = kwargs["req"]
        context = super().get_context_data(**kwargs)

        print(request.session["test_params"])

        if request.session["test_params"]["for_wX"] == 1:
            context["for_wX"] = 1
        elif request.session["test_params"]["for_wX"] == 2:
            context["for_wX"] = 2

        if request.session["test_params"]["duration"] == "finite":
            context["group_obj"] = GroupOfWords.objects.get(id=self.kwargs.get("uuid"))
            randint = random.randint(0, len(request.session["test_params"]["list_test_words"]) - 1)
            print('\n', request.session["test_params"]["list_test_words"], "\n")
            random_word_id = request.session["test_params"]["list_test_words"].pop(randint)
            request.session.modified = True
            print('\n', request.session["test_params"]["list_test_words"], "\n")
            context["word_obj"] = Word.objects.get(id=random_word_id)
            return context

        elif request.session["test_params"]["duration"] == "loop":
            context["group_obj"] = GroupOfWords.objects.get(id=self.kwargs.get("uuid"))
            context["word_obj"] = random.choice(context["group_obj"].words.all())
            return context

    def form_valid(self, form):
        if form.is_valid():
            word_obj = Word.objects.get(id=self.request.POST.getlist("word_obj")[0])
            input_word = self.request.POST.getlist("input_word")[0]
            compare_with = None
            if self.request.session["test_params"]["for_wX"] == 1:
                compare_with = word_obj.word2
            elif self.request.session["test_params"]["for_wX"] == 2:
                compare_with = word_obj.word1

            print(f"\nI COMPARE {compare_with} WITH {input_word}\n")

            if compare_with == input_word:
                messages.success(self.request,
                                 f'Answer "{input_word}" is correct. Translation of "{word_obj.word1}" is '
                                 f'"{word_obj.word2}"')
                if self.request.session["test_params"]["test_eval"] == "ranked":
                    word_obj.score += 1
                    res_obj = Result.objects.get(id=self.request.session["test_params"]["result_id"])
                    if self.request.session["test_params"]["duration"] == "finite":
                        res_obj.details["test_words"][f"{str(word_obj.id)}"]["input_word"] = input_word
                        res_obj.details["test_words"][f"{str(word_obj.id)}"]["is_correct"] = True
                        res_obj.save()

            elif compare_with != input_word:
                messages.success(self.request,
                                 f'Answer "{input_word}" is incorrect. Correct translation of "{word_obj.word1}" is '
                                 f'"{word_obj.word2}"')
                if self.request.session["test_params"]["test_eval"] == "ranked":
                    word_obj.score -= 1
                    if self.request.session["test_params"]["duration"] == "finite":
                        res_obj = Result.objects.get(id=self.request.session["test_params"]["result_id"])
                        res_obj.details["test_words"][f"{str(word_obj.id)}"]["input_word"] = input_word
                        res_obj.details["test_words"][f"{str(word_obj.id)}"]["is_correct"] = False
                        res_obj.save()

            word_obj.save()

            return redirect(
                reverse_lazy(f"words:groups_of_words_test", kwargs={'uuid': self.kwargs["uuid"]}))


class TestsResultsListView(ListView):
    model = Result
    context_object_name = 'results'
    template_name = "tests/results_list.html"


class TestsResultView(DetailView):
    pk_url_kwarg = "uuid"
    model = Result
    context_object_name = "result"
    template_name = "tests/single_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dict_details = Result.objects.get(id=self.kwargs["uuid"]).details

        # print(f"\nDETAILS DICT{dict_details}\n")
        # print(f"\n{dict_details['test_words'].keys()}\n")

        context_dict = {"test_words": {}}
        for key in dict_details["test_words"].keys():
            print(f"\nWe take {key}")
            context_dict["test_words"][f'{Word.objects.get(id=key).word1} - {Word.objects.get(id=key).word2}'] = \
                dict_details["test_words"][key]
            # print("\n", dict_details["test_words"], "\n")
        context["dict"] = context_dict
        print(context_dict)
        return context
