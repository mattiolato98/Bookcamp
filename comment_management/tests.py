from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import now

from book_management.models import Book, Author
from comment_management.forms import InsertCommentCrispyForm
from comment_management.models import Topic, Comment


class TopicPageViewTest(TestCase):
    """
    Test della View 'TopicPageView'.
    """

    def setUp(self):
        """
        Setup di un ambiente di test. Crea i seguenti oggetti a scopo di test:
            - Utente
            - Autore
            - Libro
            - Topic
        :return:
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.author = Author.objects.create(name="Autore di prova")
        self.book = Book.objects.create(
            title="Libro di prova",
            publisher="Editore di prova",
            year="2020",
            language="Italiano",
            isbn_10="1234567890",
            isbn_13="1234567890123",
        )

        self.book.authors.add(self.author)

        self.topic = Topic.objects.create(
            user_owner=self.user,
            book=self.book,
            title="Topic di prova",
            message="Messagio di prova",
            creation_date_time=now(),
            last_modified_date_time=now(),
        )

    def test_topic_page_view_comments_list_user_owner_of_topic_GET(self):
        """
        Test della GET della pagina con utente proprietario del topic.
        """
        comment = Comment.objects.create(
            user_owner=self.user,
            topic=self.topic,
            message="Commento di prova",
            creation_date_time=now(),
        )

        response = self.client.get(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}))
        self.assertEquals(response.status_code, 200)

        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}))
        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, 'comment_management/view_topic.html')
        self.assertNotContains(response, "Nessun commento presente")
        self.assertContains(response, "Salvataggi")

        self.assertEquals(response.context['topic'], self.topic)
        self.assertEquals(response.context['form'], InsertCommentCrispyForm)
        self.assertQuerysetEqual(response.context['object_list'], ['<Comment: john>'])

    def test_topic_page_view_comments_list_empty_GET(self):
        """
        Test della GET della pagina con utente non loggato e lista dei commenti vuota.
        """
        response = self.client.get(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}))
        self.assertEquals(response.status_code, 200)

        self.assertContains(response, "Nessun commento presente")
        self.assertNotContains(response, "Salvataggi")

    def test_topic_page_view_comments_list_user_not_owner_of_topic_GET(self):
        """
        Test della GET della pagina con utente NON proprietario del topic.
        """
        user = get_user_model().objects.create_user('utente', 'utente@mail.com', 'utentepassword')
        self.client.login(username='utente', password='utentepassword')

        response = self.client.get(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}))
        self.assertEquals(response.status_code, 200)

        self.assertContains(response, "Nessun commento presente")
        self.assertNotContains(response, "Salvataggi")

    def test_topic_page_view_new_comment_POST(self):
        """
        Test della POST della pagina con utente loggato.
        """
        data = {
            'message': 'Commento di prova POST',
        }

        self.client.login(username='john', password='johnpassword')

        response = self.client.post(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}), data=data)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(Comment.objects.filter(topic_id=self.topic.pk).count(), 1)
        self.assertEquals(self.topic.comments_count, 1)
        self.assertEquals(Comment.objects.get(message='Commento di prova POST').user_owner, self.user)

    def test_topic_page_view_new_comment_user_not_logged_in_POST(self):
        """
        Test della POST della pagina con utente NON loggato.
        """
        data = {
            'message': 'Commento di prova POST',
        }

        response = self.client.post(reverse('comment_management:view-topic', kwargs={'pk': self.topic.pk}), data=data)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(Comment.objects.filter(topic_id=self.topic.pk).count(), 0)
        self.assertEquals(self.topic.comments_count, 0)
        self.assertEquals(Comment.objects.filter(message='Commento di prova POST').count(), 0)


class AjaxSaveLikeTest(TestCase):
    """
    Test della funzione Ajax 'ajax_save_like'
    """

    def setUp(self):
        """
         Setup di un ambiente di test. Crea i seguenti oggetti a scopo di test:
            - Utente
            - Autore
            - Libro
            - Topic
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.author = Author.objects.create(name="Autore di prova")
        self.book = Book.objects.create(
            title="Libro di prova",
            publisher="Editore di prova",
            year="2020",
            language="Italiano",
            isbn_10="1234567890",
            isbn_13="1234567890123",
        )

        self.book.authors.add(self.author)

        self.topic = Topic.objects.create(
            user_owner=self.user,
            book=self.book,
            title="Topic di prova",
            message="Messagio di prova",
            creation_date_time=now(),
            last_modified_date_time=now(),
        )

    def test_ajax_save_like_POST(self):
        """
        Test della POST con utente loggato.
        """
        data = {
            'topic_primary_key': self.topic.pk,
        }

        self.client.login(username='john', password='johnpassword')
        response = self.client.post(reverse('comment_management:ajax-save-like'), data=data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Topic.objects.get(pk=self.topic.pk).likes.count(), self.topic.likes_count)
        self.assertEquals(self.topic.likes_count, 1)

    def test_ajax_save_like_user_not_logged_in_POST(self):
        """
        Test della POST con utente NON loggato.
        """
        data = {
            'topic_primary_key': self.topic.pk,
        }

        response = self.client.post(reverse('comment_management:ajax-save-like'), data=data)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Topic.objects.get(pk=self.topic.pk).likes.count(), self.topic.likes_count)
        self.assertEquals(self.topic.likes_count, 0)
