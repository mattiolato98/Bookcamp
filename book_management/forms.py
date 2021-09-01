from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms


class NewBookCrispyForm(forms.Form):
    """
    Form utilizzato per inserire un nuovo libro.
    Campi:
        - isbn
    """
    helper = FormHelper()
    helper.form_id = 'new-book-crispy-form'
    helper.form_method = 'POST'
    helper.add_input(Button('search', 'Cerca',
                            css_id='new-book-search-button',
                            css_class='btn site-btn-yellow site-btn-small mb-2 mt-4'))
    helper.add_input(Submit('submit', 'Inserisci libro',
                            css_id="new-book-submit-button",
                            css_class='btn site-btn mb-2 mt-4 w-25 book-found'))

    isbn = forms.CharField(label="", max_length=50, required=True, widget=forms.TextInput(
        attrs={'class': 'w-50 mt-5 light-input', 'placeholder': 'ISBN', 'id': 'isbn-code'}))