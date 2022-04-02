import isbnlib

from googletrans import LANGUAGES
from isbnlib import NotValidISBNError


class BookData:
    """
    Manage book metadata.
    """
    isbn = None
    book = None
    metadata = {}

    def __init__(self, isbn):
        """
        Initialize book metadata starting from its ISBN code.
        :param isbn: isbn_10 or isbn_13 code of the book
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
        :return: Book metadata.
        """
        return self.metadata
