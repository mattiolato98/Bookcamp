from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from django.core.files import File
from django.db import models
from django.db.models import Count, Avg
from django.utils.translation import gettext_lazy as _

import comment_management


class Author(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=150)
    authors = models.ManyToManyField(Author, related_name="book_authors")

    publisher = models.CharField(max_length=150, blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    language = models.CharField(max_length=5, blank=True, null=True)
    cover_image_file = models.ImageField(default='books_cover/default/default_cover.png',
                                         upload_to='books_cover/')
    cover_image_url = models.URLField(blank=True, null=True)

    isbn_10 = models.CharField(max_length=20)
    isbn_13 = models.CharField(max_length=20)

    def __str__(self):
        return '%s di %s' % (self.title, self.authors)

    @property
    def authors_str(self):
        """
        :return: Authors' list separated by comma.
        """
        string = ""
        book_authors = self.authors.all()

        if len(book_authors) > 0:
            string += book_authors[0].name
            for author in book_authors[1:]:
                string += ', %s' % author.name
            return string

        return None

    @property
    def authors_count(self):
        """
        :return: Book authors' number.
        """
        return self.authors.all().count()

    @property
    def average_rating(self):
        """
        :return: Average rating of the book.
        """
        average_rating = self.profile_books.exclude(rating=None).aggregate(avg_rating=Avg('rating'))['avg_rating']
        return int(average_rating) if average_rating is not None else average_rating

    @property
    def number_of_ratings(self):
        """
        :return: Number of ratings the book received.
        """
        return self.profile_books.exclude(rating=None).count()

    @property
    def people_reading_count(self):
        """
        :return: Number of people who have read the book.
        """
        return self.profile_books.exclude(status='READ').exclude(status='MUSTREAD').count()

    @property
    def topics_count(self):
        """
        :return: Number of book's Topics.
        """
        return self.topics.all().count()

    @property
    def topics_set(self):
        """
        :return: Set of book's Topics.
        """
        return self.topics.all()

    @property
    def comments_set(self):
        """
        :return: Set of comments related to the book's Topics.
        """
        topics = self.topics.all()
        return comment_management.models.Comment.objects.filter(topic__in=topics)

    @property
    def comments_count(self):
        """
        :return: Number of comments related to the book's Topics.
        """
        count = 0
        for topic in self.topics.all():
            count += topic.comments_count
        return count

    @property
    def is_top_5(self):
        """
        :return: True if the book is in the Top5, False otherwise.
        """
        return True if self in self.get_top_5() else False

    @staticmethod
    def get_top_5():
        """
        Search 5 most popular books.
        The search is based on the number of published Topics for each book.
        :return: 5 most popular books ordered by number of Topics decreasing.
        """
        return Book.objects.all().annotate(num_topics=Count('topics')).order_by('-num_topics')[:5]

    @property
    def cover_image_file_is_default(self):
        """
        :return: True if the cover image is the default, False otherwise.
        """
        return True if self.cover_image_file == self._meta.get_field('cover_image_file').get_default() else False

    def save(self, *args, **kwargs):
        """
        While saving, check if is present a cover_image_url.
        If so, download the relative image and saves it, assigning the path to the field cover_image_file.
        """
        if self.cover_image_url and self.cover_image_file == self._meta.get_field('cover_image_file').get_default():
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(self.cover_image_url).read())
            img_temp.flush()
            self.cover_image_file.save(f"book_{self.isbn_10}", File(img_temp))
        super(Book, self).save(*args, **kwargs)

