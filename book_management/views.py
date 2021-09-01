import urllib

import isbnlib
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseServerError
from django.urls import reverse_lazy
from django.views.generic import FormView

from isbnlib import NotValidISBNError
from googletrans import LANGUAGES
from book_management.forms import NewBookCrispyForm
from book_management.models import Book, Author


class BookData:
    """
    Classe per la gestione dei dati di un libro.
    """
    isbn = None
    book = None
    metadata = {}

    def __init__(self, isbn):
        """
        Inizializza i metadati del libro a partire dal suo isbn.
        :param isbn: codice isbn_10 o isbn_13 del libro
        """
        self.isbn = isbn
        try:
            self.book = isbnlib.meta(isbn)
        except NotValidISBNError:
            self.metadata = {'found': False}

        if self.book:
            language = LANGUAGES[self.book['Language']]

            image_url = ""
            has_cover_image = False
            book_cover = isbnlib.cover(self.isbn)
            if book_cover:
                image_url = book_cover['thumbnail']
                has_cover_image = True

            self.metadata = {
                'found': True,
                'has_cover_image': has_cover_image,
                'title': self.book['Title'],
                'authors': self.book['Authors'],
                'publisher': self.book['Publisher'],
                'year': self.book['Year'],
                'language': language,
                'image_url': image_url,
            }
        else:
            self.metadata = {'found': False}

    def get_metadata(self):
        """
        :return: Metadati del libro.
        """
        return self.metadata


@login_required
def ajax_search_book(request):
    """
    Funzione chiamata da AJAX per scaricare i dati di un libro.
    :param request: Richiesta AJAX.
    :return: Metadati del libro.
    """
    isbn = request.GET.get('isbn_code')

    if Book.objects.filter(isbn_10=isbnlib.to_isbn10(isbn)).exists():
        data = {
            'found': False,
            'already_exists': True,
            'book_pk': Book.objects.get(isbn_10=isbnlib.to_isbn10(isbn)).pk,
        }
        return JsonResponse(data)

    book = BookData(isbn)
    book_metadata = book.get_metadata()

    if book_metadata['found']:
        if book_metadata['has_cover_image']:
            urllib.request.urlretrieve(book_metadata['image_url'], 'static/img/book.jpeg')

        data = {
            'found': True,
            'has_cover_image': book_metadata['has_cover_image'],
            'book_title': book_metadata['title'] if book_metadata['title'] else "-",
            'book_authors': book_metadata['authors'] if book_metadata['authors'] else "-",
            'book_publisher': book_metadata['publisher'] if book_metadata['publisher'] else "-",
            'book_year': book_metadata['year'] if book_metadata['year'] else "-",
            'book_language': book_metadata['language'] if book_metadata['language'] else "-",
        }

        return JsonResponse(data)

    data = {'found': False}
    return JsonResponse(data)


class NewBookView(LoginRequiredMixin, FormView):
    """
    View per l'inserimento di un nuovo libro.
    Contiene il form NewBookCrispyForm.
    """
    template_name = 'book_management/new_book.html'
    form_class = NewBookCrispyForm
    book = None

    def form_valid(self, form):
        """
        Recupera i metadati del libro prima di validare il form.
        Se al codice isbn corrisponde un libro valido, ne viene creata l'istanza con i dati relativi.
        Se il libro non viene trovato o ne esiste già l'istanza, viene ritornato un HttpServerError.
        :return: HttpServerError se il libro esiste già o il codice isbn non corrisponde ad alcun libro valido.
        """
        isbn = form.cleaned_data['isbn']

        book_data = BookData(isbn)
        book_metadata = book_data.get_metadata()

        if book_metadata['found']:
            if not Book.objects.filter(isbn_10=isbnlib.to_isbn10(isbn)).exists():
                self.book = Book(title=book_metadata['title'],
                                 publisher=book_metadata['publisher'],
                                 year=book_metadata['year'],
                                 language=book_metadata['language'],
                                 cover_image_url=book_metadata['image_url'],
                                 isbn_10=isbnlib.to_isbn10(isbn),
                                 isbn_13=isbnlib.to_isbn13(isbn))
                self.book.save()

                for author in book_metadata['authors']:
                    if Author.objects.filter(name=author).exists():
                        a = Author.objects.get(name=author)
                    else:
                        a = Author(name=author)
                        a.save()
                    self.book.authors.add(a)
            else:
                return HttpResponseServerError()
        else:
            return HttpResponseServerError()

        return super(NewBookView, self).form_valid(form)

    def get_success_url(self):
        """
        :return: success_url con la pagina del libro appena inserito.
        """
        return reverse_lazy('view-public-book', kwargs={'pk': self.book.pk})

