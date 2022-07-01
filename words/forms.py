from django.forms import ModelForm
from .models import Word, GroupOfWords
from django import forms


class WordForm(ModelForm):
    class Meta:
        model = Word
        fields = ['word1', 'word2', "group"]


# class GroupForm(ModelForm):
#     class Meta:
#         model = GroupOfWords
#         words = forms.ModelMultipleChoiceField(Word.objects.all())
#         fields = ("name", "description", "words")

class GroupForm(forms.Form):
    name = forms.CharField(label="name")
    words = forms.ModelMultipleChoiceField(queryset=Word.objects.all(), widget=forms.CheckboxSelectMultiple())


    # def save(self, commit=True):
    #     group = super().save(Commit=False)


class GroupFilterForm(forms.Form):
    groups = forms.ModelMultipleChoiceField(queryset=GroupOfWords.objects.all(), widget=forms.CheckboxSelectMultiple())