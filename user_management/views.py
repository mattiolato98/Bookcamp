from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView, FormView
from django.utils.translation import gettext_lazy as _

from books_base_folder.views import SearchMixin
from book_management.decorators import profile_book_exists_only
from user_management.forms import UpdateBookInfoCrispyForm
from book_management.models import Book
from user_management.decorators import has_profile_only, has_not_profile_only
from user_management.forms import PlatformUserCreationForm, LoginForm, UpdateProfileCrispyForm, CreateProfileCrispyForm, \
    UpdateProfilePictureCrispyForm, SearchBookCrispyForm, UpdatePasswordCrispyForm
from user_management.models import Profile, ProfileBook

account_activation_token = PasswordResetTokenGenerator()


class UserCreateView(CreateView):
    """
    User CreateView.
    It contains PlatformUserCreationForm.
    """
    form_class = PlatformUserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('user_management:email-verification-needed')

    def form_valid(self, form):
        """
        Completes the User creation, deactivating the User and sending a confirmation email.
        """
        response = super(UserCreateView, self).form_valid(form)

        mail_subject = _('Bookcamp, email di conferma account')
        relative_confirm_url = reverse(
            'user_management:verify-user-email',
            args=[
                urlsafe_base64_encode(force_bytes(self.object.pk)),
                account_activation_token.make_token(self.object)
            ]
        )

        self.object.email_user(
            subject=mail_subject,
            message=_(f'''Ciao {self.object.username}, '''
                      + '''ti diamo il benvenuto in Bookcamp.\n'''
                      + '''\nClicca il seguente link per confermare la tua email:'''
                      + f'''\n{self.request.build_absolute_uri(relative_confirm_url)}\n'''
                      + '''\nA presto, \nil Team di Bookcamp.''')
        )

        self.object.token_sent = True
        self.object.is_active = False
        self.object.save()

        return response


def user_login_by_token(request, user_id_b64=None, user_token=None):
    """
    Checks if the token matches that of the User trying to verify the email.
    """
    try:
        uid = force_str(urlsafe_base64_decode(user_id_b64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, user_token):
        user.is_active = True
        user.save()
        login(request, user)
        return True

    return False


def verify_user_email(request, user_id_b64=None, user_token=None):
    """
    :return: Email successfully verified page, if the token matches that of the User.
    """
    if not user_login_by_token(request, user_id_b64, user_token):
        message = _('Errore. Tentativo di validazione email per l\'utente {user} con token {token}')

    return redirect('user_management:email-verified')


class LoginUserView(LoginView):
    """
    Login View.
    It contains LoginForm.
    """
    form_class = LoginForm
    template_name = "registration/login.html"
    success_url = reverse_lazy('home')


class EmailVerificationNeededView(TemplateView):
    template_name = 'user_management/email_verification_needed.html'


class EmailVerifiedView(LoginRequiredMixin, TemplateView):
    template_name = 'user_management/email_verified.html'


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = "comment_management/report.html"


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    Profile TemplateView.
    """
    template_name = "user_management/user_profile.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects to a different page if the User has not a Profile and it is not the owner of the Profile.
        """
        user_obj = get_user_model().objects.get(pk=self.kwargs['pk'])
        if not user_obj.has_profile and not user_obj == self.request.user:
            self.template_name = "user_management/profile_not_exists.html"
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Retrieves User info.
        """
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['user_for_profile'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context


@method_decorator([login_required, has_not_profile_only], name='dispatch')
class CreateProfileView(CreateView):
    """
    Profile CreateView.
    It contains CreateProfileCrispyForm.
    """
    form_class = CreateProfileCrispyForm
    template_name = 'user_management/create_profile.html'

    def form_valid(self, form):
        """
        Collects needed info to complete the Profile creation.
        """
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.pk
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-profile' of the just created Profile.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateProfileView(UpdateView):
    """
    Profile UpdateView.
    It contains UpdateProfileCrispyForm.
    """
    model = Profile
    form_class = UpdateProfileCrispyForm
    template_name = "user_management/update_profile.html"

    def get_object(self, queryset=None):
        """
        Retrieves Profile object of the requesting User.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-profile' of the just created Profile.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateProfilePictureView(UpdateView):
    """
    Profile picture UpdateView.
    It contains UpdateProfilePictureCrispyForm.
    """
    model = Profile
    form_class = UpdateProfilePictureCrispyForm
    template_name = "user_management/update_profile_picture.html"

    def get_object(self, queryset=None):
        """
        Retrieves Profile object of the requesting User.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)

    def get_success_url(self):
        """
        :return: redirect towards the page 'view-profile' of the just created Profile.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


class ProfileSettingsView(LoginRequiredMixin, TemplateView):
    """
    Profile settings TemplateView.
    """
    template_name = "user_management/user_settings.html"


class UpdatePasswordView(LoginRequiredMixin, UpdateView):
    """
    Password UpdateView.
    """
    model = get_user_model()
    template_name = "user_management/update_password.html"
    form_class = UpdatePasswordCrispyForm

    def get_object(self, queryset=None):
        """
        Retrieves Profile object of the requesting User.
        """
        return get_user_model().objects.get(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        """
        Manages redirection when the cancel button is clicked.
        """
        if "cancel" in request.POST:
            url = reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})
            return HttpResponseRedirect(url)
        return super(UpdatePasswordView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Checks that the old password matches.
        """
        if self.request.user.check_password(form.cleaned_data['old_password']):
            return super(UpdatePasswordView, self).form_valid(form)
        else:
            return HttpResponseBadRequest()

    def get_success_url(self):
        """
        :return: redirect towards the page 'login' of the User that has just updated the password.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class FollowingUsersListView(TemplateView):
    """
    Following Users ListView.
    """
    model = Profile
    template_name = "user_management/following_users_list.html"


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """
    User DeleteView.
    """
    model = get_user_model()
    template_name = "user_management/delete_user.html"
    success_url = reverse_lazy("user_management:login")

    def get_object(self, queryset=None):
        """
        Retrieves User object of the requesting User.
        """
        return get_user_model().objects.get(pk=self.request.user.pk)


class DeleteProfileView(LoginRequiredMixin, DeleteView):
    """
    Profile DeleteView.
    """
    model = Profile
    template_name = 'user_management/delete_profile.html'
    success_url = reverse_lazy('user_management:user-settings')

    def get_object(self, queryset=None):
        """
        Retrieves Profile object of the requesting User.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)


class BookshelfView(LoginRequiredMixin, FormView):
    """
    Bookshelf FormView.
    """
    template_name = "user_management/bookshelf/bookshelf.html"
    form_class = SearchBookCrispyForm

    def get_context_data(self, **kwargs):
        """
        Retrieves User info.
        """
        context = super(BookshelfView, self).get_context_data(**kwargs)
        context['user_for_profile'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Checks that the User has completed his Profile. Otherwise, shows an error page.
        """
        user_obj = get_user_model().objects.get(pk=self.kwargs['pk'])
        if not user_obj.has_profile:
            self.template_name = "user_management/profile_not_exists.html"
        return super(BookshelfView, self).dispatch(request, *args, **kwargs)


@method_decorator([login_required, has_profile_only], name='dispatch')
class BookshelfNewBook(SearchMixin, FormView):
    """
    Bookshelf book insertion View. It shows a list of books based on a search query.
    """
    template_name = "user_management/bookshelf/bookshelf_new_book.html"
    form_class = SearchBookCrispyForm

    def get_context_data(self, **kwargs):
        """
        Updates Crispy Form search bar style and adds the query as the default value.
        Filters out the books already present in the requesting User Bookshelf.
        """
        context = super(BookshelfNewBook, self).get_context_data(**kwargs)

        context['form'].fields['search'].widget.attrs.update({'class': 'light-input'})

        if context['search_query'] is not None:
            context['form'].fields['search'].widget.attrs.update({'value': context['search_query']})

        if context['books'] is not None:
            context['books'] = context['books'].exclude(id__in=self.request.user.profile.books_set)

        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateReadingBooks(TemplateView):
    """
    Books being read list. It allows moving or deleting them.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Set READING as type.
        """
        context = super(UpdateReadingBooks, self).get_context_data(**kwargs)
        context['type'] = "READING"
        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateReadBooks(TemplateView):
    """
    Books read list. It allows moving or deleting them.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Set READ as type.
        """
        context = super(UpdateReadBooks, self).get_context_data(**kwargs)
        context['type'] = "READ"
        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateMustReadBooks(TemplateView):
    """
    Books to read list. It allows moving or deleting them.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Set MUSTREAD as type.
        """
        context = super(UpdateMustReadBooks, self).get_context_data(**kwargs)
        context['type'] = "MUSTREAD"
        return context


@method_decorator([login_required, has_profile_only, profile_book_exists_only], name='dispatch')
class UpdateBookInfo(UpdateView):
    template_name = 'user_management/bookshelf/update_book_info.html'
    form_class = UpdateBookInfoCrispyForm

    def get_object(self, queryset=None):
        """
        Retrieves ProfileBook object.
        """
        return ProfileBook.objects.get(profile_owner_id=self.request.user.profile.pk, book_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(UpdateBookInfo, self).get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['pk'])

        if self.get_object().status == 'READING':
            context['form'].fields['end_reading_date'].widget.attrs['disabled'] = True
            context['form'].fields['rating'].widget.attrs['disabled'] = True
            context['error_message'] = 'Sposta in libri letti per poter inserire una data di fine lettura e un voto'
        if self.get_object().status == 'MUSTREAD':
            context['form'].fields['start_reading_date'].widget.attrs['disabled'] = True
            context['form'].fields['end_reading_date'].widget.attrs['disabled'] = True
            context['form'].fields['rating'].widget.attrs['disabled'] = True
            context['error_message'] = 'Sposta in libri in lettura o letti per poter inserire una data di inizio e ' \
                                       'fine lettura e un voto'

        return context

    def form_valid(self, form):
        """
        Checks that disabled fields have not been filled.
        """
        if self.get_object().status == 'READING' and \
                (form.fields['end_reading_date'] is not None or form.fields['rating'] is not None):
            self.object = form.save(commit=False)
            self.object.rating = None
            self.object.end_reading_date = None
            self.object.save()
        if self.get_object().status == 'MUSTREAD' and \
                (form.fields['start_reading_date'] is not None or form.fields['end_reading_date']
                 or form.fields['rating'] is not None):
            self.object = form.save(commit=False)
            self.object.rating = None
            self.object.start_reading_date = None
            self.object.end_reading_date = None
            self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('view-private-book', kwargs={'pk': self.kwargs['pk']})


@login_required
@require_POST
@csrf_protect
def ajax_save_follow(request):
    """
    Ajax called function to save a Follow.
    It receives a User pk. Checks if the requesting User is already present in the follower list of the other User:
        - if so, it takes it off the follow
        - otherwise it adds the follow
    :return: Boolean value, True if the Follow has been added, False otherwise.
    """
    user_pk = request.POST.get('user')
    profile = Profile.objects.get(user_id=user_pk)

    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        return JsonResponse({
            'followed': False
        })

    profile.followers.add(request.user)
    return JsonResponse({
        'followed': True
    })


def ajax_check_username_exists(request):
    """
    Ajax called function to check if a username is present in the Database.
    :return: True, if the Username already exists, False otherwise.
    """
    return JsonResponse({'exists': True}) \
        if get_user_model().objects.filter(username=request.GET.get('username')).exists() \
        else JsonResponse({'exists': False})


@login_required
@require_POST
@csrf_protect
def ajax_delete_book(request):
    """
    Ajax called function to delete a Book from the Bookshelf.
    :return:
        - Deleted Book pk
        - 'deleted' state
    """
    book_id = request.POST.get('book_primary_key')
    ProfileBook.objects.get(profile_owner=request.user.profile, book_id=book_id).delete()

    return JsonResponse({
        'id': book_id,
        'status': 'deleted'
    })


@login_required
@require_POST
@csrf_protect
def ajax_move_book(request):
    """
    Ajax called function to move a Book in the Bookshelf.
    It is necessary to use the save method instead of update to change the rating.
    :return:
        - Moved Book pk
        - Book state
    """
    book_id = request.POST.get('book_primary_key')
    move_to = request.POST.get('move_to')

    profile_book = ProfileBook.objects.get(profile_owner=request.user.profile, book_id=book_id)
    profile_book.status = move_to
    profile_book.save()

    status = ProfileBook.objects.get(book_id=book_id, profile_owner_id=request.user.profile.pk).get_verbose_status

    return JsonResponse({
            'id': book_id,
            'status': status,
        })


@login_required
@require_POST
@csrf_protect
def ajax_new_book(request):
    """
    Ajax called function to insert a new Book in the Bookshelf.
    :return: Inserted Book state.
    """
    book_id = request.POST.get('book_primary_key')
    move_to = request.POST.get('move_to')

    profile_book = ProfileBook(
        profile_owner=request.user.profile,
        book_id=book_id,
        status=move_to,
    )
    profile_book.save()

    status = ProfileBook.objects.get(book_id=book_id, profile_owner_id=request.user.profile.pk).get_verbose_status

    return JsonResponse({
            'status': status,
        })
