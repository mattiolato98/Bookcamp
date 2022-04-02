from django.template.defaulttags import register

from user_management.models import ProfileBook, Profile


@register.filter
def user_saved_book(book, user):
    """
    Check if user has saved the book in his Bookshelf.
    :param book: Book object.
    :param user: PlatformUser object.
    :return: True if the user has saved the book, False otherwise.
    """
    return ProfileBook.objects.filter(book_id=book.pk, profile_owner_id=user.profile.pk).exists()


@register.filter
def get_user_book_status(book, user):
    """
    Return book status in the user's bookshelf.
    :param book: Book object.
    :param user: PlatformUser object.
    :return: Book status.
    """
    return ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).get_verbose_status


@register.filter
def user_rated_book(book, user):
    """
    Check if the user has rated the book in his own bookshelf.
    :param book: Book object.
    :param user: PlatformUser object.
    :return: True if the book has been rated, False otherwise.
    """
    return True if ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).rating is not None\
        else False


@register.filter
def get_user_book_rating(book, user):
    """
    Return book rating in the user bookshelf.
    :param book: Book object.
    :param user: PlatformUser object.
    :return: Book rating.
    """
    return ProfileBook.objects.get(book_id=book.pk, profile_owner_id=user.profile.pk).rating
