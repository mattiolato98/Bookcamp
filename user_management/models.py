from collections import defaultdict
from datetime import date

from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from book_management.models import Book
from comment_management.models import Topic, Bookmark


class PlatformUser(AbstractUser):
    AbstractUser._meta.get_field('email')._unique = True

    # terms_of_service_acceptance = models.BooleanField(default=False)
    # terms_of_service_acceptance_datetime = models.DateTimeField(auto_now_add=True)

    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def has_profile(self):
        """
        Checks if the user has an associated profile.
        :return: True if the user has an associated profile, False otherwise.
        """
        try:
            assert self.profile
            return True
        except ObjectDoesNotExist:
            return False

    @property
    def topics_set(self):
        """
        :return: User Topics set.
        """
        return self.topics.all()

    @property
    def topics_count(self):
        """
        :return: User Topics number.
        """
        return self.topics.all().count()

    @property
    def comments_set(self):
        """
        :return: User Comments set.
        """
        return self.comments.all()

    @property
    def comments_set_group_by_book(self):
        """
        :return: User comments set, grouped by book.
            Dictionary in the form {Book: [Comment list]}
        """
        comments = self.comments.all().order_by('-creation_date_time', 'topic__book')

        comments_group_by_book = defaultdict(list)
        for comment in comments:
            comments_group_by_book[comment.topic.book].append(comment)

        return comments_group_by_book

    @property
    def comments_count(self):
        """
        :return: User Comments number.
        """
        return self.comments.all().count()

    @property
    def likes_count(self):
        """
        :return: Number of Likes put by the User.
        """
        return self.likes.all().count()

    @property
    def saved_topics_set(self):
        """
        :return: User saved Topics set, ordered by inverse creation date.
        """
        bookmarks = self.bookmarks.all()
        return Topic.objects.filter(bookmarks__in=bookmarks).order_by('-bookmarks__creation_date_time')

    @property
    def liked_topics_set(self):
        """
        :return: Topics set liked by the User, ordered by inverse creation date.
        """
        likes = self.likes.all()
        return Topic.objects.filter(likes__in=likes).order_by('-likes__creation_date_time')

    @property
    def bookmarks_count(self):
        """
        :return: User Bookmarks number.
        """
        return self.bookmarks.all().count()

    @staticmethod
    def get_popular_by_topics():
        """
        :return: 5 most popular Users based on published Topics.
        """
        return PlatformUser.objects.all().annotate(num_topics=Count('topics')).order_by('-num_topics')\
            .exclude(profile=None)[:5]

    @staticmethod
    def get_popular_by_comments():
        """
        :return: 5 most popular Users based on published Comments.
        """
        return PlatformUser.objects.all().annotate(num_comments=Count('comments')).order_by('-num_comments')\
            .exclude(profile=None)[:5]

    @property
    def get_followed_profiles(self):
        """
        :return: List of Profile followed by the User, ordered by start follow date decreasing.
        """
        return self.followed_profiles.all().order_by('-follower_relations__starting_follow_date_time')

    # def clean(self):
    #     """
    #     Checks that Terms of Service have been accepted. Otherwise it denies User creation.
    #     """
    #     if not self.terms_of_service_acceptance:
    #         raise ValidationError(_('È necessario accettare i termini di servizio per proseguire.'))


class Profile(models.Model):
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
        :return: Complete name.
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def books_count(self):
        """
        :return: Number of books in the User Bookshelf.
        """
        return self.books.all().count()

    @property
    def books_set(self):
        """
        :return: Book list in the User Bookshelf, ordered by:
                    1. Reading end date decreasing
                    2. Reading start date decreasing
                    3. Last update date decreasing
        """
        books = self.books.all()
        return Book.objects.filter(profile_books__in=books).\
            order_by('-profile_books__end_reading_date',
                     '-profile_books__start_reading_date', '-profile_books__last_update_date_time')

    @property
    def books_set_for_shelf(self):
        """
        :return: Book list in the User Bookshelf, excluding those without cover. Results are ordered by:
                    1. Reading end date decreasing
                    2. Reading start date decreasing
                    3. Last update date decreasing
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
        Adjust profile picture size in order to make it a square.
        Sets the default image if no one has been added.
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
    user_following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following_relations",
                                       on_delete=models.CASCADE)
    profile_followed = models.ForeignKey(Profile, related_name="follower_relations", on_delete=models.CASCADE)
    starting_follow_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s segue %s" % (self.user_following.username, self.profile_followed.user.username)


class ProfileBook(models.Model):
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
        Book state human readable.
        """
        if self.status == 'READ':
            return _("Letto")
        if self.status == 'READING':
            return _("In lettura")
        if self.status == 'MUSTREAD':
            return _("Da leggere")

    def save(self, *args, **kwargs):
        """
        Final checks before save. Make some changes if necessary.
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
        A User can read a Book at most once.
        """
        unique_together = ["profile_owner", "book"]
        ordering = ['-last_update_date_time', ]
