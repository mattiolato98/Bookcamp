import isbnlib
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseServerError
from django.urls import reverse_lazy
from django.views.generic import FormView

from book_management.forms import NewBookCrispyForm
from book_management.models import Book, Author
from book_management.utils import BookData


@login_required
def ajax_search_book(request):
    """
    Function called by Ajax to download book data.
    :param request: Ajax request.
    :return: Book metadata.
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
    New book creation view.
    Contains the NewBookCrispyForm form.
    """
    template_name = 'book_management/new_book.html'
    form_class = NewBookCrispyForm
    book = None

    def form_valid(self, form):
        """
        Retrieve book metadata before validating the form.
        If the ISBN code is associated with a book, it is instantiated with related data.
        If the book is not found or the instance already exists, returns HttpServerError.
        :return: HttpServerError if the book already exists or the ISBN code does not correspond to any book.
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
        :return: success_url with the page of the book just created.
        """
        return reverse_lazy('view-public-book', kwargs={'pk': self.book.pk})

