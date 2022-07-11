from django.forms import ModelForm, ModelMultipleChoiceField
from .models import Word, GroupOfWords
from django import forms


class WordForm(ModelForm):
    class Meta:
        model = Word
        fields = ['word1', 'word2', "group"]


class GroupForm(ModelForm):

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only members of the current user
        are given as options"""
        self.request = kwargs.pop('request')
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['words'].queryset = Word.objects.filter(
            user=self.request.user)

    class Meta:
        model = GroupOfWords
        fields = ("name", "description", "words")

    words = ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple, required=False)


# class GroupForm(forms.Form):
#
#     def __init__(self, **kwargs):
#         super().__init__()
#         self.request = kwargs.pop("request")
#
#     def get_request(self):
#         return self.request
#
#     request = get_request()
#     name = forms.CharField(label="name")
#     words = forms.ModelMultipleChoiceField(queryset=request.user.groups_of_words.all(),
#                                            widget=forms.CheckboxSelectMultiple())

# def save(self, commit=True):
#     group = super().save(Commit=False)


class GroupFilterForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=GroupOfWords.objects.all(), widget=forms.CheckboxSelectMultiple())


# class QuickTestForm(forms.Form)
def qs_not_empty(query_set):
    return False if query_set.words.count() == 0 else True


class GroupChoiceForm(forms.Form):

    def __init__(self, user, *args, **kwargs, ):
        super(GroupChoiceForm, self).__init__(*args, **kwargs)
        self.user = user
        groups_qs = GroupOfWords.objects.filter(user=self.user)
        for group in groups_qs:
            if not qs_not_empty(group):
                groups_qs = groups_qs.exclude(id=group.id)
        # filtered_groups_qs = filter(qs_not_empty, groups_qs)
        # print(list(filtered_groups_qs))
        self.fields['groups'].queryset = groups_qs

    # class Meta:
    #     model = GroupOfWords
    #     fields = ("name", "words")

    groups = forms.ModelChoiceField(queryset=None)


# class TestInputForm(ModelForm):
#     class Meta:
#         model = Word
#         fields = ("word1",)

class TestInputForm(forms.Form):
    input_word = forms.CharField()


class TestParametersForm(forms.Form):

    def __init__(self, user, *args, **kwargs, ):
        super(TestParametersForm, self).__init__(*args, **kwargs)
        self.user = user
        groups_qs = GroupOfWords.objects.filter(user=self.user)
        for group in groups_qs:
            if not qs_not_empty(group):
                groups_qs = groups_qs.exclude(id=group.id)
        self.fields['groups'].queryset = groups_qs

    duration_choices = (("loop", "Loop"), ("finite", "Finite"))
    type_choices = (("ranked", "Ranked"), ("unranked", "Unranked"))
    test_for_choices = (
        ("for_w1", "Word1 to Word2"), ("for_w2", "Word2 to Word1"))

    groups = forms.ModelChoiceField(queryset=None)
    durations = forms.ChoiceField(choices=duration_choices)
    type = forms.ChoiceField(choices=type_choices)
    test_for_translation_of = forms.ChoiceField(choices=test_for_choices)
