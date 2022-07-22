from django.core.validators import MinLengthValidator
from django.forms import ModelForm, ModelMultipleChoiceField
from .models import Word, GroupOfWords
from django import forms


class WordForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(WordForm, self).__init__(*args, **kwargs)
        self.fields['groups'].queryset = GroupOfWords.objects.filter(
            user=self.request.user).exclude(name="General")

    word1 = forms.CharField(validators=[MinLengthValidator(1)])
    groups = ModelMultipleChoiceField(queryset=None,
                                      widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Word
        fields = ['word1', 'word2']


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

    duration_choices = (("", "---------"), ("loop", "Loop"), ("finite", "Finite"))
    type_choices = (("", "---------"), ("ranked", "Ranked"), ("unranked", "Unranked"))
    test_for_choices = (("", "---------"),
                        ("for_w1", "Word1 to Word2"), ("for_w2", "Word2 to Word1"))
    do_with_incorrect_choices = (("", "---------"), ("skip", "Skip"), ("repeat", "Repeat"))
    lower_score_first_choices = (("", "---------"), ("lower_score_first", "Words with lower are asked firstly"),
                                 ("random_score_first", "Random word picked"))

    help_text_groups = "A 'Group', all words of which will be included in the test."
    help_text_durations = "'Loop' for infinite test for words of a group. If 'Finite' is chosen, test will end, after all answers will be submitted, result will be created."
    help_text_type = "'Ranked' for answer will change the score, If 'Unranked', score won't be affected."
    help_text_test_for_translation_of = "'A user's choice defines translation of what word will be asked."
    help_text_do_with_incorrect = "If 'repeat' is chosen, test won't end until all answers are answered correctly."
    help_text_lower_score_first = "Pick 'Words with lower are asked firstly' if ypu want to test words with lower score"
    groups = forms.ModelChoiceField(queryset=None, help_text=help_text_groups)
    durations = forms.ChoiceField(choices=duration_choices,
                                  help_text=help_text_durations)
    type = forms.ChoiceField(choices=type_choices, help_text=help_text_type)
    test_for_translation_of = forms.ChoiceField(choices=test_for_choices, help_text=help_text_test_for_translation_of)
    do_with_incorrect = forms.ChoiceField(choices=do_with_incorrect_choices, help_text=help_text_do_with_incorrect)
    lower_score_first = forms.ChoiceField(choices=lower_score_first_choices, help_text=help_text_lower_score_first)
