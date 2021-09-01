from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from comment_management.models import Topic, Comment


class NewTopicCrispyForm(forms.ModelForm):
    """
    Form per l'inserimento di un nuovo topic.
    Campi:
        - title
        - message
    """
    helper = FormHelper()
    helper.form_id = 'new-topic-crispy-form'
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'mt-5 light-input w-75',
            'placeholder': 'Titolo'
        })

    class Meta:
        model = Topic
        fields = ("title", "message")
        labels = {
            'title': '',
            'message': '',
        }


class UpdateTopicCrispyForm(forms.ModelForm):
    """
    Form per l'update di un topic.
    Campi:
        - title
        - message
    """
    helper = FormHelper()
    helper.form_id = 'update-topic-crispy-form'
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'light-input',
            'placeholder': 'Titolo'
        })

    class Meta:
        model = Topic
        fields = ('title', 'message')
        labels = {
            'title': 'Titolo',
            'message': 'Messaggio',
        }


class InsertCommentCrispyForm(forms.ModelForm):
    """
    Form per l'inserimento di un nuovo commento.
    Campi:
        - message
    """
    helper = FormHelper()
    helper.form_id = 'insert-comment-crispy-form'
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Commenta', css_class='btn site-btn'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({
            'id': 'new-comment-field',
            'class': 'w-100 ',
            'placeholder': 'Aggiungi un commento ...',
            'rows': '3',
            'style': 'resize: none;'
        })

    class Meta:
        model = Comment
        fields = {'message'}
        labels = {
            'message': '',
        }
