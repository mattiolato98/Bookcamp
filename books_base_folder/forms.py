from crispy_forms.helper import FormHelper
from django import forms


class SearchCrispyForm(forms.Form):
    """
    Form that provide site search engine.

    Fields:
        - search
    """
    helper = FormHelper()
    helper.form_id = 'search-crispy-form'
    helper.form_method = 'GET'
    helper.form_class = "w-100"

    search = forms.CharField(label="", required=False, max_length=50, widget=forms.TextInput(
        attrs={'class': 'search-input shadow', 'placeholder': 'Cerca ...', 'id': 'search-bar'}))