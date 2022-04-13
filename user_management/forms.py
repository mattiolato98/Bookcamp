from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy

from user_management.models import Profile, ProfileBook


class PlatformUserCreationForm(UserCreationForm):
    """
    Form to create a PlatformUser.

    Fields:
        - username
        - email
        - password1
        - password2
    """
    helper = FormHelper()
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            # 'terms_of_service_acceptance',
        )
        # labels = {
        #     'terms_of_service_acceptance': 'Termini e Condizioni',
        # }


class LoginForm(AuthenticationForm):
    """
    Login form.
    """
    helper = FormHelper()


class CreateProfileCrispyForm(forms.ModelForm):
    """
    Form to create a Profile.

    Fields:
        - picture
        - first_name
        - last_name
        - description
    """
    helper = FormHelper()
    helper.form_id = 'create-profile-crispy-form'
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'class': 'light-input'})
        self.fields['last_name'].widget.attrs.update({'class': 'light-input'})
        self.fields['description'].widget.attrs.update({'style': 'resize: none;'})

        self.helper.layout = Layout(
            Row(
              Column('picture', css_class='form-group mb-3'),
              css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group mb-0'),
                Column('last_name', css_class='form-group mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('description', css_class='form-group mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = Profile
        fields = (
            'picture',
            'first_name',
            'last_name',
            'description',
        )
        labels = {
            'picture': 'Immagine del profilo',
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'description': 'Descrizione',
        }


class UpdateProfileCrispyForm(forms.ModelForm):
    """
    Form to update a Profile.

    Fields:
        - first_name
        - last_name
        - description
    """
    helper = FormHelper()
    helper.form_id = 'update-profile-crispy-form'
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'class': 'light-input'})
        self.fields['last_name'].widget.attrs.update({'class': 'light-input'})
        self.fields['description'].widget.attrs.update({'style': 'resize: none;'})

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group mb-0'),
                Column('last_name', css_class='form-group mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('description', css_class='form-group mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'description',
        )
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'description': 'Descrizione',
        }


class UpdateProfilePictureCrispyForm(forms.ModelForm):
    """
    Form to update profile picture.

    Fields:
        - picture
    """
    helper = FormHelper()
    helper.form_id = 'update-profile-picture-crispy-form'
    helper.form_method = 'POST'

    class Meta:
        model = Profile
        fields = 'picture',
        labels = {'picture': 'Immagine del profilo'}


class UpdatePasswordCrispyForm(UserCreationForm):
    """
    Form to update the password.

    Fields:
        - old_password
        - new_password_1
        - new_password_2
    """
    helper = FormHelper()
    helper.form_id = 'update-password-crispy-form'
    helper.form_method = 'POST'

    old_password = forms.CharField(label="Vecchia password", required=True, max_length=128, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs.update({'class': 'light-input', 'placeholder': 'Vecchia password'})
        self.fields['password1'].widget.attrs.update({'class': 'light-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.\
            update({'class': 'light-input', 'placeholder': 'Conferma password'})

        self.helper.layout = Layout(
            Row(
                Column('old_password', css_class='form-group mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group mb-0'),
                Column('password2', css_class='form-group mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = get_user_model()
        fields = (
            'password1',
            'password2',
        )


class SearchBookCrispyForm(forms.Form):
    """
    Form to search books.

    Fields:
        - search
    """
    helper = FormHelper()
    helper.form_id = 'search-book-crispy-form'
    helper.form_method = 'GET'
    helper.form_class = "w-100"
    helper.form_action = reverse_lazy('user_management:bookshelf-new-book', kwargs={})

    search = forms.CharField(label="", required=False, max_length=50, widget=forms.TextInput(
        attrs={'class': 'search-input shadow', 'placeholder': 'Cerca ...', 'id': 'search-bar'}))


class UpdateBookInfoCrispyForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = 'update-book-info-crispy-form'
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'class': 'light-input', 'placeholder': 'Voto', 'max': 100, 'min': 0})

        self.helper.layout = Layout(
            Row(
                Column('start_reading_date', css_class='form-group mb-0'),
                Column('end_reading_date', css_class='form-group mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('rating', css_class='form-group mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = ProfileBook
        fields = (
            'start_reading_date',
            'end_reading_date',
            'rating',
        )
        labels = {
            'start_reading_date': 'Data di inizio lettura',
            'end_reading_date': 'Data di fine lettura',
            'rating': 'Voto (0-100)',
        }
        widgets = {
            'start_reading_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'light-input'}),
            'end_reading_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'light-input'}),
        }
