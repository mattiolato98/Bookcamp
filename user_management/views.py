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
    View per la creazione di un utente.
    Contiene il form PlatformUserCreationForm.
    """
    form_class = PlatformUserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('user_management:email-verification-needed')

    def form_valid(self, form):
        """
        Completa l'inserimento disattivando l'utente e inviando una mail di conferma.
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
    Verifica che il token corrisponda a quello dell'utente che sta cercando di verifica la mail.
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
    :return: Pagina di email verificata con successo, se il token corrisponde a quello dell'utente.
    """
    if not user_login_by_token(request, user_id_b64, user_token):
        message = _('Errore. Tentativo di validazione email per l\'utente {user} con token {token}')

    return redirect('user_management:email-verified')


class LoginUserView(LoginView):
    """
    View per il login.
    Contiene il form LoginForm.
    """
    form_class = LoginForm
    template_name = "registration/login.html"
    success_url = reverse_lazy('home')


class EmailVerificationNeededView(TemplateView):
    """
    View per la visualizzazione della pagina 'Verifica email necessaria'.
    """
    template_name = 'user_management/email_verification_needed.html'


class EmailVerifiedView(LoginRequiredMixin, TemplateView):
    """
    View per la visualizzazione della pagina 'Email verificata con successo'.
    """
    template_name = 'user_management/email_verified.html'


class ReportView(LoginRequiredMixin, TemplateView):
    """
    View per la visualizzazione della pagina 'Report'.
    """
    template_name = "comment_management/report.html"


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    View per la visualizzazione del profilo di un utente.
    """
    template_name = "user_management/user_profile.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Reindirizza a un template differente se l'utente richiesto non ha un profilo e a fare richiesta
        è un utente non proprietario.
        """
        user_obj = get_user_model().objects.get(pk=self.kwargs['pk'])
        if not user_obj.has_profile and not user_obj == self.request.user:
            self.template_name = "user_management/profile_not_exists.html"
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Recupera le informazioni dell'utente e di tutti i libri.
        """
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['user_for_profile'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context


@method_decorator([login_required, has_not_profile_only], name='dispatch')
class CreateProfileView(CreateView):
    """
    View per la creazione di un profilo
    Contiene il form CreateProfileCrispyForm.
    """
    form_class = CreateProfileCrispyForm
    template_name = 'user_management/create_profile.html'

    def form_valid(self, form):
        """
        Raccoglie le informazioni necessarie a completare l'inserimento.
        """
        self.object = form.save(commit=False)
        self.object.user_id = self.request.user.pk
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'view-profile' del profilo appena creato. 
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateProfileView(UpdateView):
    """
    View per la modifica di un profilo.
    Contiene il form UpdateProfileCrispyForm.
    """
    model = Profile
    form_class = UpdateProfileCrispyForm
    template_name = "user_management/update_profile.html"

    def get_object(self, queryset=None):
        """
        Recupera l'oggetto profilo dell'utente che fa richiesta.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'view-profile' del profilo appena modificato.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateProfilePictureView(UpdateView):
    """
    View per la modifica dell'immagine del profilo.
    Contiene il form UpdateProfilePictureCrispyForm.
    """
    model = Profile
    form_class = UpdateProfilePictureCrispyForm
    template_name = "user_management/update_profile_picture.html"

    def get_object(self, queryset=None):
        """
        Recupera l'oggetto profilo dell'utente che fa richiesta.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'view-profile' del profilo appena modificato.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


class ProfileSettingsView(LoginRequiredMixin, TemplateView):
    """
    View per la visualizzazione delle impostazioni di un utente.
    """
    template_name = "user_management/user_settings.html"


class UpdatePasswordView(LoginRequiredMixin, UpdateView):
    """
    View per la modifica della password dell'utente.
    """
    model = get_user_model()
    template_name = "user_management/update_password.html"
    form_class = UpdatePasswordCrispyForm

    def get_object(self, queryset=None):
        """
        Recupera l'oggetto profilo dell'utente che fa richiesta.
        """
        return get_user_model().objects.get(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        """
        Gestisce redirezione in caso di pressione del pulsante 'cancel'.
        """
        if "cancel" in request.POST:
            url = reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})
            return HttpResponseRedirect(url)
        return super(UpdatePasswordView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Verifica che la vecchia password inserita sia corretta.
        """
        if self.request.user.check_password(form.cleaned_data['old_password']):
            return super(UpdatePasswordView, self).form_valid(form)
        else:
            return HttpResponseBadRequest()

    def get_success_url(self):
        """
        :return: redirect verso la pagina 'login' dell'utente che ha appena modificato la password.
        """
        return reverse_lazy('user_management:view-profile', kwargs={'pk': self.request.user.pk})


@method_decorator([login_required, has_profile_only], name='dispatch')
class FollowingUsersListView(TemplateView):
    """
    View per la visualizzazione dell'elenco dei profili seguiti da un utente.
    """
    model = Profile
    template_name = "user_management/following_users_list.html"


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """
    View per l'eliminazione di un utente.
    """
    model = get_user_model()
    template_name = "user_management/delete_user.html"
    success_url = reverse_lazy("user_management:login")

    def get_object(self, queryset=None):
        """
        Recupera l'oggetto utente dell'utente che fa richiesta.
        """
        return get_user_model().objects.get(pk=self.request.user.pk)


class DeleteProfileView(LoginRequiredMixin, DeleteView):
    """
    View per l'eliminazione di un profilo.
    """
    model = Profile
    template_name = 'user_management/delete_profile.html'
    success_url = reverse_lazy('user_management:user-settings')

    def get_object(self, queryset=None):
        """
        Recupera l'oggetto profilo dell'utente che fa richiesta.
        """
        return Profile.objects.get(pk=self.request.user.profile.pk)


class BookshelfView(LoginRequiredMixin, FormView):
    """
    View per la visualizzazione di un bookshelf.
    """
    template_name = "user_management/bookshelf/bookshelf.html"
    form_class = SearchBookCrispyForm

    def get_context_data(self, **kwargs):
        """
        Recupera le informazioni dell'utente e dei suoi libri.
        """
        context = super(BookshelfView, self).get_context_data(**kwargs)
        context['user_for_profile'] = get_user_model().objects.get(pk=self.kwargs['pk'])
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Verifica che l'utente di cui si sta tentando di vedere il bookshelf, abbia completato il proprio profilo.
        Alternativamente visualizza una pagina di errore.
        """
        user_obj = get_user_model().objects.get(pk=self.kwargs['pk'])
        if not user_obj.has_profile:
            self.template_name = "user_management/profile_not_exists.html"
        return super(BookshelfView, self).dispatch(request, *args, **kwargs)


@method_decorator([login_required, has_profile_only], name='dispatch')
class BookshelfNewBook(SearchMixin, FormView):
    """
    View per la visualizzazione di una lista di libri in base alla query di ricerca, con la possibilità di
    inserirli nel bookshelf in una delle categorie.
    """
    template_name = "user_management/bookshelf/bookshelf_new_book.html"
    form_class = SearchBookCrispyForm

    def get_context_data(self, **kwargs):
        """
        Aggiorna lo stile della barra di ricerca del Crispy Form e aggiunge la query come valore di default.
        Filtra il context rimuovendo i libri già presenti nella libreria dell'utente che sta facendo richiesta.
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
    View per la visualizzazione della lista di libri in lettura, con la possibilità di spostarli o eliminarli.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Setta READING come type.
        """
        context = super(UpdateReadingBooks, self).get_context_data(**kwargs)
        context['type'] = "READING"
        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateReadBooks(TemplateView):
    """
    View per la visualizzazione della lista di libri letti, con la possibilità di spostarli o eliminarli.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Setta READ come type.
        """
        context = super(UpdateReadBooks, self).get_context_data(**kwargs)
        context['type'] = "READ"
        return context


@method_decorator([login_required, has_profile_only], name='dispatch')
class UpdateMustReadBooks(TemplateView):
    """
    View per la visualizzazione della lista di libri da leggere, con la possibilità di spostarli o eliminarli.
    """
    template_name = "user_management/bookshelf/update_bookshelf.html"

    def get_context_data(self, **kwargs):
        """
        Setta MUSTREAD come type.
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
        Recupera l'oggetto ProfileBook.
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
        Verifica che i campi disabilitati non siano stati riempiti.
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
    Funzione chiamata da Ajax per salvare un follow.
    Riceve la pk di un utente. Verifica se l'utente che fa richiesta è già presente nella lista di seguaci dell'utente
    passato:
        - in caso affermativo lo elimina (l'utente sta cercando di smettere di seguire)
        - alternativamente lo aggiunge (l'utente sta cercando di iniziare a seguire)
    :return: Booleano indicante se l'utente ha iniziato o smesso di seguire.
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
    Funzione chiamata da Ajax per verifica la presenza di uno username tra le istanze.
    :return: Booleano indicante se lo username esiste già.
    """
    return JsonResponse({'exists': True}) \
        if get_user_model().objects.filter(username=request.GET.get('username')).exists() \
        else JsonResponse({'exists': False})


@login_required
@require_POST
@csrf_protect
def ajax_delete_book(request):
    """
    Funzione chiamata da Ajax per eliminare un libro dal bookshelf.
    :return: id del libro eliminato, status eliminato del libro.
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
    Funzione chiamata da Ajax per spostare un libro nel bookshelf.
    Necessario usare il metodo save e non update per modificare il rating.
    :return: id del libro spostato, status attuale del libro (dove è stato spostato).
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
    Funzione chiamata da Ajax per inserire un nuovo libro nel bookshelf.
    :return: id del libro inserito, status attuale del libro (dove è stato inserito).
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
