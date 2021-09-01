from django.template.defaulttags import register

from user_management.models import ProfileBook, Profile


@register.filter
def user_saved_book(book, user):
    """
    Verifica se l'utente ha salvato il libro nel suo Bookshelf.
    :param book: Oggetto Book.
    :param user: Oggetto PlatformUser.
    :return: True se l'utente ha salvato il libro, False altrimenti
    """
    return ProfileBook.objects.filter(book_id=book.pk, profile_owner_id=user.profile.pk).exists()


@register.filter
def get_user_book_status(book, user):
    """
    Ritorna lo status del libro nel bookshelf dell'utente.
    :param book: Oggetto Book.
    :param user: Oggetto PlatformUser.
    :return: Status del libro relativo all'utente.
    """
    return ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).get_verbose_status


@register.filter
def user_rated_book(book, user):
    """
    Verifica se l'utente ha o meno valutato il libro nel suo bookshelf.
    :param book: Oggetto Book.
    :param user: Oggetto PlatformUser.
    :return: True se il libro è stato valutato, False altrimenti.
    """
    return True if ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).rating is not None\
        else False


@register.filter
def get_user_book_rating(book, user):
    """
    Ritorna il rating del libro nel bookshelf dell'utente.
    :param book: Oggetto Book.
    :param user: Oggetto PlatformUser.
    :return: Rating del libro relativo all'utente.
    """
    return ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).rating
