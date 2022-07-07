import django_filters
from django import forms

from words.models import Word, GroupOfWords


def groups(request):
    if request is None:
        return GroupOfWords.objects.none()
    return request.user.groups_of_words.all()


class WordFilter(django_filters.FilterSet):
    group = django_filters.ModelMultipleChoiceFilter(queryset=groups, widget=forms.CheckboxSelectMultiple())
    # score__lt = django_filters.NumberFilter(field_name="score", lookup_expr="et")
    # name_sw = django_filters.CharFilter(field_name="word1", lookup_expr="startswith")

    # score__gt = django_filters.NumberFilter(field_name="score")
    class Meta:
        model = Word
        fields = {"score": ["lt", "gt"]}
