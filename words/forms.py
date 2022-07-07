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
        fields = ("name", "words")

    words = ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple)


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

class GroupChoiceForm(forms.Form):

    def __init__(self, user, *args, **kwargs, ):
        super(GroupChoiceForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['groups'].queryset = GroupOfWords.objects.filter(
            user=self.user)

    class Meta:
        model = GroupOfWords
        fields = ("name", "words")

    groups = forms.ModelChoiceField(queryset=None)


class TestInputForm(ModelForm):
    class Meta:
        model = Word
        fields = ("word1",)
