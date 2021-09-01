import bleach as bleach

from django.conf import settings
from django.db import models

from book_management.models import Book
from tinymce import models as tinymce_models


class Topic(models.Model):
    """
    Model che contiene i dati di un topic.
    """
    user_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topics")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="topics", null=True, blank=True)

    title = models.CharField(max_length=150, default="")
    message = tinymce_models.HTMLField(max_length=10000, default="")

    creation_date_time = models.DateTimeField(auto_now_add=True)
    last_modified_date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s di %s" % (self.title, self.user_owner.username)

    @property
    def likes_count(self):
        """
        :return: Numero di like del topic.
        """
        return self.likes.all().count()

    @property
    def bookmarks_count(self):
        """
        :return: Numero di salvataggi del topic.
        """
        return self.bookmarks.all().count()

    @property
    def comments_count(self):
        """
        :return: Numero di commenti del topic.
        """
        return self.comments.all().count()

    @property
    def comments_set(self):
        """
        :return: Set di commenti relativi al topic.
        """
        return self.comments.all()

    def clean(self):
        """
        Pulisce il campo message da tag non autorizzati. Questo previene eventuali errori in visualizzazione
        nel momento in cui il messaggio verrà renderizzato nella pagina.
        I tag permessi sono presenti nella lista tags.
        Gli attributi permessi sono presenti nella lista attrs.
        Gli stili permessi sono presenti nella lista styles.
        """
        tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'p', 'br', 'span', 'code', 'em', 'i', 'li', 'ol',
                'strong', 'ul', 'b', 'abbr']
        attrs = {
            '*': ['style'],
            'abbr': ['title'],
        }
        styles = ['background-color', 'text-align']

        self.message = bleach.clean(self.message,
                                    tags=tags,
                                    attributes=attrs,
                                    styles=styles,
                                    strip=True)

        super(Topic, self).clean()

    class Meta:
        """
        Ordine decrescente per pk (ultimo inserito per primo)
        """
        ordering = ['-pk', ]


class Comment(models.Model):
    """
    Model che contiene i dati di un commento.
    """
    user_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)

    message = models.TextField(max_length=5000, default="")

    creation_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_owner.username


class Like(models.Model):
    """
    Model che contiene i dati di un like.
    """
    user_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    creation_date_time = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)

    def __str__(self):
        return self.user_owner.username

    class Meta:
        """
        Un utente può mettere mi piace a un topic al più una volta.
        """
        unique_together = ["user_owner", "topic"]


class Bookmark(models.Model):
    """
    Model che contiene i dati di un salvataggio.
    """
    user_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="bookmarks")
    creation_date_time = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="bookmarks", null=True, blank=True)

    def __str__(self):
        return self.user_owner.username

    class Meta:
        """
        Un utente può salvare un topic al più una volta.
        """
        unique_together = ["user_owner", "topic"]