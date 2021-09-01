from datetime import datetime, date

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Count

from django.utils.translation import gettext_lazy as _

from book_management.models import Book
from comment_management.models import Topic, Bookmark


class PlatformUser(AbstractUser):
    """
    Model contenente gli utenti.
    """
    AbstractUser._meta.get_field('email')._unique = True

    # terms_of_service_acceptance = models.BooleanField(default=False)
    # terms_of_service_acceptance_datetime = models.DateTimeField(auto_now_add=True)

    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def has_profile(self):
        """
        Verifica se l'utente ha un profilo associato.
        :return: True se l'utente ha un profilo associato, False altrimenti.
        """
        try:
            assert self.profile
            return True
        except ObjectDoesNotExist:
            return False

    @property
    def topics_set(self):
        """
        :return: Set dei topic dell'utente.
        """
        return self.topics.all()

    @property
    def topics_count(self):
        """
        :return: Numero di topic dell'utente.
        """
        return self.topics.all().count()

    @property
    def comments_set(self):
        """
        :return: Set dei commenti dell'utente.
        """
        return self.comments.all()

    @property
    def comments_set_group_by_book(self):
        """
        :return: Set dei commenti dell'utente, raggruppati per libro. Dizionario del tipo {Book: [Lista di Comment]}
        """
        comments = self.comments.all().order_by('-creation_date_time', 'topic__book')

        # inizializza il dizionario con chiave: lista_vuota
        comments_group_by_book = {comment.topic.book: [] for comment in comments}
        for comment in comments:
            comments_group_by_book[comment.topic.book].append(comment)  # riempie le liste con i commenti

        return comments_group_by_book

    @property
    def comments_count(self):
        """
        :return: Numero di commenti dell'utente.
        """
        return self.comments.all().count()

    @property
    def likes_count(self):
        """
        :return: Numero di like messi dall'utente.
        """
        return self.likes.all().count()

    @property
    def saved_topics_set(self):
        """
        :return: Set di topic salvati dall'utente in ordine inverso di crazione (dall'ultimo salvato).
        """
        bookmarks = self.bookmarks.all()
        return Topic.objects.filter(bookmarks__in=bookmarks).order_by('-bookmarks__creation_date_time')

    @property
    def liked_topics_set(self):
        """
        :return: Set di topic a cui l'utente ha messo mi piace in ordine inverso di creazione (dall'ultimo piaciuto).
        """
        likes = self.likes.all()
        return Topic.objects.filter(likes__in=likes).order_by('-likes__creation_date_time')

    @property
    def bookmarks_count(self):
        """
        :return: Numero di bookmark dell'utente.
        """
        return self.bookmarks.all().count()

    @staticmethod
    def get_popular_by_topics():
        """
        :return: 5 utenti più popolari sulla base dei topic pubblicati.
        """
        return PlatformUser.objects.all().annotate(num_topics=Count('topics')).order_by('-num_topics')\
            .exclude(profile=None)[:5]

    @staticmethod
    def get_popular_by_comments():
        """
        :return: 5 utenti più popolari sulla base dei commenti pubblicati.
        """
        return PlatformUser.objects.all().annotate(num_comments=Count('comments')).order_by('-num_comments')\
            .exclude(profile=None)[:5]

    @property
    def get_followed_profiles(self):
        """
        :return: Lista dei profili seguiti dall'utente, in ordine decrescente di data di inizio follow
         (da quello seguito per ultimo).
        """
        return self.followed_profiles.all().order_by('-follower_relations__starting_follow_date_time')

    # def clean(self):
    #     """
    #     Verifica che siano stati accettati i Termini di servizio. In caso contrario nega la creazione dell'utente.
    #     """
    #     if not self.terms_of_service_acceptance:
    #         raise ValidationError(_('È necessario accettare i termini di servizio per proseguire.'))


class Profile(models.Model):
    """
    Model contenente i profili.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    description = models.TextField(max_length=10000, blank=True, null=True)
    picture = models.ImageField(upload_to='profiles/images/%Y/%m/%d',
                                default="profiles/default/default_profile_image.jpg",
                                blank=True, null=True)

    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="followed_profiles",
                                       through="FollowRelation")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return "%s (%s)" % (self.get_name, self.user.username)

    @property
    def get_name(self):
        """
        :return: Nome completo.
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def books_count(self):
        """
        :return: Numero di libri nel bookshelf dell'utente.
        """
        return self.books.all().count()

    @property
    def books_set(self):
        """
        :return: Elenco dei libri nel bookshelf dell'utente, risultati ordinati per:
                    1. data di fine lettura decrescente
                    2. data di inizio lettura decrescente
                    3. data di ultima modifica decrescente
        """
        books = self.books.all()
        return Book.objects.filter(profile_books__in=books).\
            order_by('-profile_books__end_reading_date',
                     '-profile_books__start_reading_date', '-profile_books__last_update_date_time')

    @property
    def books_set_for_shelf(self):
        """
        :return: Elenco dei libri nel booshelf dell'utente, escludendo quelli senza
                    copertina e ordinando i risultati per:
                        1. data di fine lettura decrescente
                        2. data di inizio lettura decrescente
                        3. data di ultima modifica decrescente
        """
        books = self.books.all().exclude(book__cover_image_file__exact=Book._meta.get_field('cover_image_file').default)
        return Book.objects.filter(profile_books__in=books).\
            order_by('-profile_books__end_reading_date', '-profile_books__start_reading_date',
                     '-profile_books__last_update_date_time')

    @property
    def reading_books_set(self):
        books = self.books.filter(status='READING')
        return Book.objects.filter(profile_books__in=books).order_by('-profile_books__start_reading_date')

    @property
    def read_books_set(self):
        books = self.books.filter(status='READ')
        return Book.objects.filter(profile_books__in=books).order_by('-profile_books__end_reading_date')

    @property
    def must_read_books_set(self):
        books = self.books.filter(status='MUSTREAD')
        return Book.objects.filter(profile_books__in=books).order_by('-profile_books__last_update_date_time')

    def save(self, *args, **kwargs):
        """
        Completa il salvataggio modificando l'immagine del profilo in modo da renderla un quadrato.
        Se non è presente nessuna immagine setta quella di default (utile in caso di eliminazione
        dell'immagine in fase di update).
        """
        super().save()
        if self.picture:
            img = Image.open(self.picture.path)
            width, height = img.size

            if width > 300 and height > 300:
                img.thumbnail((width, height))

            if height < width:
                left = (width - height) / 2
                right = (width + height) / 2
                top = 0
                bottom = height
                img = img.crop((left, top, right, bottom))

            elif width < height:
                left = 0
                right = width
                top = 0
                bottom = width
                img = img.crop((left, top, right, bottom))

            if width > 300 and height > 300:
                img.thumbnail((300, 300))

            img.save(self.picture.path)
        else:
            self.picture = self._meta.get_field('picture').get_default()
            self.save()


class FollowRelation(models.Model):
    """
    Model contenente la relazione di Follow tra un utente e un profilo.
    """
    user_following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following_relations",
                                       on_delete=models.CASCADE)
    profile_followed = models.ForeignKey(Profile, related_name="follower_relations", on_delete=models.CASCADE)
    starting_follow_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s segue %s" % (self.user_following.username, self.profile_followed.user.username)


class ProfileBook(models.Model):
    """
    Model che contiene i libri di un profilo, nelle tre categorie:
        - In lettura
        - Letti
        - Da leggere
    """
    READING = 'READING'
    READ = 'READ'
    MUST_READ = 'MUSTREAD'

    BOOK_STATUS_CHOICES = [
        (READING, _("In lettura")),
        (READ, _("Letto")),
        (MUST_READ, _("Da leggere")),
    ]

    profile_owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="profile_books", null=True, blank=True)
    creation_date_time = models.DateTimeField(auto_now_add=True)
    last_update_date_time = models.DateTimeField(auto_now=True)

    start_reading_date = models.DateField(null=True, blank=True)
    end_reading_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=8, choices=BOOK_STATUS_CHOICES, default=READ)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MaxValueValidator(100)])

    def __str__(self):
        return "%s - %s" % (self.profile_owner.user.username, self.book.title)

    @property
    def get_verbose_status(self):
        """
        Status del libro human readable.
        """
        if self.status == 'READ':
            return _("Letto")
        if self.status == 'READING':
            return _("In lettura")
        if self.status == 'MUSTREAD':
            return _("Da leggere")

    def save(self, *args, **kwargs):
        """
        Esegue una serie di verifiche sull'oggetto salvato ed effettua eventuali modifiche se necessario.
        """
        if self.status != 'READ':
            self.rating = None

        if self.status == 'READING':
            if self.start_reading_date is None:
                self.start_reading_date = date.today()
            self.end_reading_date = None
        if self.status == 'READ':
            if self.end_reading_date is None:
                self.end_reading_date = date.today()
        if self.status == 'MUSTREAD':
            self.start_reading_date = None
            self.end_reading_date = None

        if self.start_reading_date is not None and self.end_reading_date is not None:
            if self.start_reading_date > self.end_reading_date:
                self.start_reading_date = self.end_reading_date

        super(ProfileBook, self).save(*args, **kwargs)

    class Meta:
        """
        Un utente può leggere un libro al più una volta.
        """
        unique_together = ["profile_owner", "book"]
        ordering = ['-last_update_date_time', ]