import django_filters

from words.models import Word


class WordFilter(django_filters.FilterSet):

    # def __init__(self, user):
    #     super().__init__(self, user)
    #     # self.a = self.request.user
    # CHOICES = (("A","a"), ("B","b"))

    # filtering = django_filters.ChoiceFilter(label="Group", choices=CHOICES, method="filter_by_group")

    class Meta:
        model = Word
        fields = ("group",)

    # def filter_by_group(self, queryset, name, value):
    #
    #     return queryset.
