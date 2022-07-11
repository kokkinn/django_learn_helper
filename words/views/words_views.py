from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.detail import SingleObjectMixin

from words.filters import WordFilter
from words.models import Word, GroupOfWords

from words.forms import WordForm

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView


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


def delete_view(request, uuid):
    word_object = Word.objects.get(id=uuid)
    if request.method == "POST":
        word_object.delete()
        return redirect(reverse_lazy("words:list"))
    context = {"word": word_object}
    return render(request, "words/delete.html", context)
